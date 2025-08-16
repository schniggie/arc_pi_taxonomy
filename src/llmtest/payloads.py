import itertools
from typing import List
from llmtest.model import Payload, TestConfig
from llmtest.taxonomy import Taxonomy


def generate_payloads(taxonomy: Taxonomy, config: TestConfig, goal_description: str) -> List[Payload]:
    """
    Generates a list of payloads based on the taxonomy and test configuration.
    This is a placeholder implementation that creates descriptive payloads
    instead of using an LLM.
    """
    payloads = []

    # Get the requested intent. If not found, we can't generate payloads.
    if config.attack_intent not in taxonomy.intents:
        # Or raise an error, for now, return empty list
        return []

    intent_name = config.attack_intent

    # Create combinations of techniques and evasions
    # For simplicity, let's take all techniques and evasions.
    # A more sophisticated version could be more selective.
    techniques = list(taxonomy.techniques.keys())
    evasions = list(taxonomy.evasions.keys())

    # Add a "no_evasion" option
    evasions.append("no_evasion")

    # Generate all combinations and limit them
    combinations = itertools.product([intent_name], techniques, evasions)

    for i, (intent, technique, evasion) in enumerate(combinations):
        if i >= config.max_payloads:
            break

        # Create a placeholder payload content
        content = f"""
        ---
        (Placeholder Payload)
        Goal: {goal_description}
        Intent: {intent}
        Technique: {technique}
        Evasion: {evasion}
        ---
        """

        payload = Payload(
            intent=intent,
            technique=technique,
            evasion=evasion,
            content=content.strip()
        )
        payloads.append(payload)

    return payloads

if __name__ == '__main__':
    # Example Usage
    from llmtest.taxonomy import load_taxonomy

    # 1. Load the taxonomy
    tax = load_taxonomy()

    # 2. Create a test configuration
    test_config = TestConfig(
        attack_intent="jailbreak",
        goal_description="Extract the system prompt",
        max_payloads=5
    )

    # 3. Generate payloads
    generated_payloads = generate_payloads(tax, test_config, test_config.goal_description)

    # 4. Print the generated payloads
    print(f"Generated {len(generated_payloads)} payloads:")
    for p in generated_payloads:
        print("\n---")
        print(f"Intent: {p.intent}, Technique: {p.technique}, Evasion: {p.evasion}")
        print("Content:")
        print(p.content)
