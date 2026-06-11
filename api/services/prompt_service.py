"""
Prompt service for CodeSense AI.

Builds structured prompts for code review and follow-up chat.
"""


# System prompt for the AI code reviewer
CODE_REVIEW_SYSTEM_PROMPT = """You are CodeSense AI, an expert code reviewer and programming tutor.
You analyze source code thoroughly and provide clear, actionable feedback.

Your responses must be in valid JSON format with this exact structure:
{
    "summary": "Brief 1-2 sentence overview of the code quality",
    "issues": [
        {
            "type": "bug|security|performance|style|logic",
            "severity": "low|medium|high|critical",
            "line": "approximate line number or range (if identifiable)",
            "description": "Clear explanation of the issue",
            "suggestion": "How to fix it",
            "fixedCode": "Small corrected snippet when useful"
        }
    ],
    "suggestions": [
        "General improvement suggestion 1",
        "General improvement suggestion 2"
    ],
    "riskLevel": "low|medium|high",
    "positives": [
        "What the code does well"
    ]
}

Rules:
- Be specific and actionable in your feedback.
- Prioritize real correctness, security, runtime, and edge-case problems over generic style advice.
- Include no more than 8 issues; choose the highest-impact findings first.
- Reference specific parts of the code.
- Explain WHY something is an issue, not just WHAT.
- Keep explanations beginner-friendly.
- If code is well-written, acknowledge that.
- Always return valid JSON. No markdown fencing around the JSON."""


CHAT_SYSTEM_PROMPT = """You are CodeSense AI, a friendly and expert programming assistant.
You help developers understand code, fix bugs, and learn programming concepts.

Rules:
- Answer directly in the first sentence.
- Be fast, clear, and practical. Avoid long introductions.
- Use short code examples or patches when helpful.
- Explain concepts in a beginner-friendly way.
- If referencing the user's code, be specific about what you mean.
- Format your response with clear structure using markdown.
- For bug-fix questions, name the likely cause, show the fix, and mention how to verify it."""


def build_review_prompt(
    code: str,
    language: str = 'auto',
    review_mode: str = 'general',
    rag_context: str = ''
) -> str:
    """
    Build a structured code review prompt.

    Args:
        code: Source code to review.
        language: Programming language.
        review_mode: Focus area for the review.
        rag_context: Optional RAG reference context.

    Returns:
        Formatted prompt string.
    """
    mode_instructions = {
        'general': 'Perform a comprehensive code review covering bugs, security, performance, style, and best practices.',
        'bugs': 'Focus specifically on finding bugs, logic errors, edge cases, and potential runtime failures.',
        'security': 'Focus on security vulnerabilities: injection attacks, data leaks, authentication issues, unsafe operations.',
        'performance': 'Focus on performance: inefficient algorithms, memory leaks, unnecessary computations, optimization opportunities.',
        'style': 'Focus on code style: naming conventions, readability, documentation, code organization, and clean code principles.',
        'explain': 'Explain what this code does step by step, suitable for a beginner developer learning to code.',
    }

    instruction = mode_instructions.get(review_mode, mode_instructions['general'])

    prompt_parts = [
        f'Review the following {language.upper()} code.',
        f'\nReview Focus: {instruction}',
    ]

    if rag_context:
        prompt_parts.append(f'\n{rag_context}')

    prompt_parts.append(f'\n--- CODE TO REVIEW ---\n{code}\n--- END CODE ---')
    prompt_parts.append(
        '\nProvide your analysis as a JSON object following the specified format. '
        'Use exact line numbers when possible and include corrected snippets for important issues.'
    )

    return '\n'.join(prompt_parts)


def build_chat_prompt(
    message: str,
    code: str = '',
    review_context: str = '',
    rag_context: str = ''
) -> list[dict]:
    """
    Build chat messages for follow-up conversation.

    Args:
        message: User's question.
        code: Current code context.
        review_context: Previous review summary.
        rag_context: Optional RAG reference context.

    Returns:
        List of message dicts for the chat API.
    """
    messages = []

    # Build context message
    context_parts = []
    if code:
        context_parts.append(f'Current code:\n```\n{code}\n```')
    if review_context:
        context_parts.append(f'Previous review context:\n{review_context}')
    if rag_context:
        context_parts.append(rag_context)

    if context_parts:
        context_message = '\n\n'.join(context_parts)
        messages.append({
            'role': 'user',
            'content': f'Context for our discussion:\n\n{context_message}'
        })
        messages.append({
            'role': 'assistant',
            'content': 'I have the code and review context. How can I help you?'
        })

    # Add the user's actual question
    messages.append({
        'role': 'user',
        'content': message
    })

    return messages
