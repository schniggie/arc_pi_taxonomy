import typer
import json
import os
import uuid
from rich.console import Console
from rich.table import Table
from typing import List, Optional

from llmtest.taxonomy import load_taxonomy
from llmtest.payloads import generate_payloads
from llmtest.execution import execute_test
from llmtest.evaluation import evaluate_response
from llmtest.model import RequestTemplate, TestConfig, ParsedRequest, TestResult
from llmtest.curl_parser import parse_curl_with_fuzz, CurlParseError, FuzzLocation

app = typer.Typer(help="A slim LLM inference testing tool for prompt injection.")
console = Console()

# --- Global State ---
state = {"debug": False}

@app.callback()
def main(
    ctx: typer.Context,
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode for verbose logging.")
):
    """
    Main callback to handle global options like --debug.
    """
    if debug:
        state["debug"] = True
        console.print("[bold yellow]Debug mode is ON[/bold yellow]")

DB_FILE = "llmtest_db.json"

def get_db_data():
    """Reads the JSON database file and returns its content."""
    if not os.path.exists(DB_FILE):
        return {"template": None, "results": []}
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"template": None, "results": []}

def write_db_data(data):
    """Writes the given data to the JSON database file."""
    try:
        with open(DB_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        console.print(f"[bold red]Error writing to database file:[/] {e}")

@app.command()
def load(
    # New curl import option
    from_curl: Optional[str] = typer.Option(None, "--from-curl", help="Load from curl command with FUZZ keywords for injection points."),

    # Existing manual options (for backward compatibility)
    url: Optional[str] = typer.Option(None, "--url", help="The target URL."),
    method: str = typer.Option("POST", "--method", "-X", help="HTTP method."),
    header: Optional[List[str]] = typer.Option(None, "--header", "-H", help="Headers in 'Key: Value' format. Can be used multiple times."),
    data: Optional[str] = typer.Option(None, "--data", "-d", help="The request body as a string."),
    inject: Optional[str] = typer.Option(None, "--inject", help="Injection point path, e.g., 'body.messages[1].content'."),
):
    """
    Load a request template either from a curl command (with FUZZ keywords) or from individual components.

    Examples:
      # Load from curl with FUZZ injection points
      llmtest load --from-curl 'curl -X POST https://api.openai.com/v1/chat/completions -H "Authorization: Bearer FUZZ" -d "{\"messages\":[{\"role\":\"user\",\"content\":\"Hello\"}]}"'

      # Load manually (legacy method)
      llmtest load --url https://api.example.com --inject "body.messages[0].content" --data '{"messages":[{"content":"test"}]}'
    """

    if from_curl:
        # New FUZZ-based curl import
        console.print("Loading request template from curl command with FUZZ detection...")

        try:
            parsed_request, fuzz_locations = parse_curl_with_fuzz(from_curl)

            if state["debug"]:
                console.print(f"\n[bold yellow]--- FUZZ Locations Detected (Debug) ---[/bold yellow]")
                for loc in fuzz_locations:
                    console.print(f"  {loc.location_type}: {loc.key} = '{loc.original_value}'")
                console.print("[bold yellow]------------------------------------[/bold yellow]\n")

            # For FUZZ-based injection, we use a special injection point format
            injection_point = "FUZZ_BASED"

            template = RequestTemplate(
                id=str(uuid.uuid4()),
                raw_request=from_curl,
                parsed_request=parsed_request,
                injection_point=injection_point,
            )

            db_data = get_db_data()
            db_data['template'] = template.model_dump()
            db_data['fuzz_locations'] = [
                {
                    'location_type': loc.location_type,
                    'key': loc.key,
                    'original_value': loc.original_value
                } for loc in fuzz_locations
            ]
            db_data['results'] = []
            write_db_data(db_data)

            console.print(f"[bold green]✓ Request template loaded from curl command.[/]")
            console.print(f"  URL: [cyan]{parsed_request.url}[/]")
            console.print(f"  Method: [cyan]{parsed_request.method}[/]")
            console.print(f"  FUZZ injection points detected: [cyan]{len(fuzz_locations)}[/]")

            for i, loc in enumerate(fuzz_locations, 1):
                console.print(f"    {i}. {loc.location_type}: [magenta]{loc.key}[/]")

        except CurlParseError as e:
            console.print(f"[bold red]✗ Failed to parse curl command:[/] {e}")
            console.print(f"[yellow]Make sure your curl command contains FUZZ keywords at injection points.[/]")
            console.print(f"[yellow]Example: curl -X POST https://api.com/chat -d '{{\"message\":\"FUZZ\"}}' [/]")
            raise typer.Exit(code=1)

    else:
        # Legacy manual loading (for backward compatibility)
        if not url:
            console.print(f"[bold red]Error:[/] Either --from-curl or --url must be provided.")
            console.print(f"[yellow]Use --from-curl for modern FUZZ-based injection or --url for legacy manual setup.[/]")
            raise typer.Exit(code=1)

        if not inject:
            console.print(f"[bold red]Error:[/] --inject is required when using manual loading (--url).")
            raise typer.Exit(code=1)

        console.print("Loading request template from components...")

        headers_dict = {}
        if header:
            for h in header:
                if ':' in h:
                    key, value = h.split(':', 1)
                    headers_dict[key.strip()] = value.strip()

        body_obj = data
        if data:
            try:
                body_obj = json.loads(data)
            except json.JSONDecodeError:
                body_obj = data

        parsed_request = ParsedRequest(
            method=method.upper(),
            url=url,
            headers=headers_dict,
            body=body_obj
        )

        raw_request_str = f"METHOD: {method}\nURL: {url}\nHEADERS: {headers_dict}\nBODY: {data}"

        template = RequestTemplate(
            id=str(uuid.uuid4()),
            raw_request=raw_request_str,
            parsed_request=parsed_request,
            injection_point=inject,
        )

        db_data = get_db_data()
        db_data['template'] = template.model_dump()
        db_data['results'] = []
        write_db_data(db_data)

        console.print(f"[bold green]✓ Request template loaded and saved.[/]")
        console.print(f"  URL: [cyan]{url}[/]")
        console.print(f"  Injection point: [cyan]{inject}[/]")

    if state["debug"]:
        from rich.pretty import pprint
        console.print("\n[bold yellow]--- Request Template (Debug) ---[/bold yellow]")
        pprint(template)
        console.print("[bold yellow]-----------------------------[/bold yellow]\n")


@app.command()
def run(
    intent: str = typer.Option(..., "--intent", help="Attack intent from the taxonomy (e.g., 'jailbreak')."),
    goal: str = typer.Option(..., "--goal", help="A description of the attack's goal."),
    max_payloads: int = typer.Option(10, "--max-payloads", help="Maximum number of payloads to generate."),
    model: str = typer.Option("z-ai/glm-4.5-air:free", "--model", help="The LLM model to use for generation and evaluation."),
):
    """
    Run an attack based on the loaded request template and a specified intent.
    """
    # Check for API key before doing anything else
    if not os.environ.get("OPENROUTER_API_KEY"):
        console.print("[bold red]Error: OPENROUTER_API_KEY environment variable not set.[/]")
        console.print("Please set the environment variable to your OpenRouter API key.")
        raise typer.Exit(code=1)

    db_data = get_db_data()

    if not db_data.get('template'):
        console.print("[bold red]No request template loaded. Please run `llmtest load` first.[/]")
        raise typer.Exit(code=1)

    request_template = RequestTemplate(**db_data['template'])
    console.print(f"Loaded request template with injection point at [cyan]{request_template.injection_point}[/]")

    console.print("Loading taxonomy...")
    taxonomy = load_taxonomy()

    test_config = TestConfig(attack_intent=intent, goal_description=goal, max_payloads=max_payloads)
    console.print(f"Generating up to {max_payloads} payloads for intent '[magenta]{intent}[/]' using model '[blue]{model}[/]'...")
    payloads = generate_payloads(taxonomy, test_config, goal, model, debug=state["debug"])
    if not payloads:
        console.print(f"[bold red]Could not generate payloads. Is the intent '{intent}' correct?[/]")
        raise typer.Exit(code=1)
    console.print(f"Generated {len(payloads)} payloads.")

    if state["debug"]:
        from rich.pretty import pprint
        console.print("\n[bold yellow]--- Generated Payloads (Debug) ---[/bold yellow]")
        for pld in payloads:
            console.print(f"Intent: {pld.intent}, Technique: {pld.technique}, Evasion: {pld.evasion}")
            console.print("Content:")
            pprint(pld.content)
            console.print("---")
        console.print("[bold yellow]--------------------------------[/bold yellow]\n")


    console.print("\n--- Starting Test Execution ---")
    results = []

    if state["debug"]:
        # In debug mode, don't use status spinner so we can see all output
        for i, pld in enumerate(payloads):
            console.print(f"\n[bold cyan]Running test {i+1}/{len(payloads)} for technique '[blue]{pld.technique}[/]'...[/]")
            try:
                console.print(f"  [yellow]Executing HTTP request...[/]")
                response = execute_test(request_template, pld, debug=True)

                console.print(f"  [yellow]HTTP Response: Status {response.status_code}[/]")
                if state["debug"] and response.status_code >= 400:
                    console.print(f"  [red]Response body: {response.text[:200]}...[/]")

                console.print(f"  [yellow]Starting evaluation...[/]")
                result = evaluate_response(response, pld, goal, model, debug=state["debug"])
                results.append(result.model_dump())

                console.print(f"  [green]✓ Test completed - Verdict: {result.verdict.value} (confidence: {result.confidence:.2f})[/]")

            except ValueError as e:
                console.print(f"  [bold red]✗ Skipping test due to error:[/] {e}")
                continue
            except Exception as e:
                console.print(f"  [bold red]✗ Unexpected error during test:[/] {e}")
                if state["debug"]:
                    import traceback
                    console.print(f"  [red]Stack trace: {traceback.format_exc()}[/]")
                continue
    else:
        # Normal mode with status spinner
        with console.status("[bold green]Running tests...[/]") as status:
            for i, pld in enumerate(payloads):
                status.update(f"Running test {i+1}/{len(payloads)} for technique '[blue]{pld.technique}[/]'...")
                try:
                    response = execute_test(request_template, pld)
                    result = evaluate_response(response, pld, goal, model, debug=state["debug"])
                    results.append(result.model_dump())
                except ValueError as e:
                    console.print(f"[bold red]Skipping test due to error:[/] {e}")
                    continue
                except Exception as e:
                    console.print(f"[bold red]Unexpected error:[/] {e}")
                    continue

    db_data['results'] = results
    write_db_data(db_data)

    console.print("\n[bold green]✓ Test run complete.[/]")
    console.print(f"Results saved to [yellow]{DB_FILE}[/]. Use `llmtest export` to view them.")

@app.command()
def export(
    format: str = typer.Option("table", "--format", help="Export format ('table' or 'json')."),
    output: str = typer.Option(None, "--output", "-o", help="Path to output file (for json format)."),
):
    """
    Export test results to the console or a file.
    """
    db_data = get_db_data()
    results_data = db_data.get('results', [])

    if not results_data:
        console.print("[yellow]No results to export.[/]")
        raise typer.Exit()

    results = [TestResult(**r) for r in results_data]

    if format == "json":
        if output:
            with open(output, 'w') as f:
                json.dump([r.model_dump() for r in results], f, indent=2)
            console.print(f"[bold green]✓ Results exported to {output}[/]")
        else:
            console.print(json.dumps([r.model_dump() for r in results], indent=2))

    elif format == "table":
        table = Table(title="Test Results")
        table.add_column("Verdict", justify="center")
        table.add_column("Confidence", justify="right")
        table.add_column("Intent", style="magenta")
        table.add_column("Technique", style="blue")
        table.add_column("Evasion", style="cyan")
        table.add_column("Response Excerpt")

        for res in results:
            verdict_color = "green" if res.verdict == "success" else "red" if res.verdict == "fail" else "yellow"
            table.add_row(
                f"[{verdict_color}]{res.verdict.value}[/{verdict_color}]",
                f"{res.confidence:.2f}",
                res.payload.intent,
                res.payload.technique,
                res.payload.evasion,
                res.response_excerpt.strip(),
            )
        console.print(table)
    else:
        console.print(f"[bold red]Invalid format '{format}'. Choose 'table' or 'json'.[/]")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
