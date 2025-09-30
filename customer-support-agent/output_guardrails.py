from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    Runner,
    output_guardrail,
)
from models import (
    AccountOutputGuardRailOutput,
    BillingOutputGuardRailOutput,
    OrderOutputGuardRailOutput,
    TechnicalOutputGuardRailOutput,
    UserAccountContext,
)

technical_output_guardrail_agent = Agent(
    name="Technical Support Guardrail",
    instructions="""
    Analyze the technical support response to check if it inappropriately contains:
    
    - Billing information (payments, refunds, charges, subscriptions)
    - Order information (shipping, tracking, delivery, returns)
    - Account management info (passwords, email changes, account settings)
    
    Technical agents should ONLY provide technical troubleshooting, diagnostics, and product support.
    Return true for any field that contains inappropriate content for a technical support response.
    """,
    output_type=TechnicalOutputGuardRailOutput,
)


@output_guardrail
async def technical_output_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent,
    output: str,
):
    result = await Runner.run(
        technical_output_guardrail_agent,
        output,
        context=wrapper.context,
    )

    validation = result.final_output

    triggered = (
        validation.contains_off_topic
        or validation.contains_billing_data
        or validation.contains_account_data
    )

    return GuardrailFunctionOutput(
        output_info=validation,
        tripwire_triggered=triggered,
    )


billing_output_guardrail_agent = Agent(
    name="Billing Support Guardrail",
    instructions="""
    Analyze the billing support response to check if it inappropriately contains:

    - Technical troubleshooting info (diagnostics, system errors, product features)
    - Account management info (passwords, email changes, security settings)

    Billing agents should ONLY provide billing, payment, subscription, and refund support.
    Return true for any field that contains inappropriate content for a billing support response.
    """,
    output_type=BillingOutputGuardRailOutput,
)


@output_guardrail
async def billing_output_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent,
    output: str,
):
    result = await Runner.run(
        billing_output_guardrail_agent,
        output,
        context=wrapper.context,
    )

    validation = result.final_output

    triggered = (
        validation.contains_off_topic
        or validation.contains_technical_data
        or validation.contains_account_data
    )

    return GuardrailFunctionOutput(
        output_info=validation,
        tripwire_triggered=triggered,
    )


account_output_guardrail_agent = Agent(
    name="Account Management Guardrail",
    instructions="""
    Analyze the account management response to check if it inappropriately contains:

    - Billing information (payments, refunds, charges, subscriptions)
    - Technical troubleshooting info (diagnostics, system errors, product features)

    Account agents should ONLY provide account access, security, and profile management support.
    Return true for any field that contains inappropriate content for an account management response.
    """,
    output_type=AccountOutputGuardRailOutput,
)


@output_guardrail
async def account_output_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent,
    output: str,
):
    result = await Runner.run(
        account_output_guardrail_agent,
        output,
        context=wrapper.context,
    )

    validation = result.final_output

    triggered = (
        validation.contains_off_topic
        or validation.contains_billing_data
        or validation.contains_technical_data
    )

    return GuardrailFunctionOutput(
        output_info=validation,
        tripwire_triggered=triggered,
    )


order_output_guardrail_agent = Agent(
    name="Order Management Guardrail",
    instructions="""
    Analyze the order management response to check if it inappropriately contains:

    - Billing information (payments, refunds, charges, subscriptions)
    - Account management info (passwords, email changes, security settings)
    - Technical troubleshooting info (diagnostics, system errors, product features)

    Order agents should ONLY provide order status, shipping, returns, and delivery support.
    Return true for any field that contains inappropriate content for an order management response.
    """,
    output_type=OrderOutputGuardRailOutput,
)


@output_guardrail
async def order_output_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent,
    output: str,
):
    result = await Runner.run(
        order_output_guardrail_agent,
        output,
        context=wrapper.context,
    )

    validation = result.final_output

    triggered = (
        validation.contains_off_topic
        or validation.contains_billing_data
        or validation.contains_account_data
        or validation.contains_technical_data
    )

    return GuardrailFunctionOutput(
        output_info=validation,
        tripwire_triggered=triggered,
    )
