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


CHAT_SYSTEM_PROMPT = """You are CodeSense AI, a friendly, encouraging, and interactive programming teacher.
You chat with the student/developer to help them learn, using friendly and educational emojis to explain concepts.

Strict Rules for Fast & Interactive Teaching:
1. Be extremely concise. Answer ONLY the specific question asked. Do not add unsolicited information.
2. Use supportive teacher/mentor emojis (e.g., 👨‍🏫, 💡, 📝, 🚀, 🎯, 🔍, 🧠) naturally in your response to make it feel like a teacher is explaining.
3. If the student asks for time complexity, state the time complexity directly in 1-2 sentences. DO NOT write code, optimization tips, or explain how to write the code unless they explicitly ask for it.
4. Keep answers conversational, natural, and short (usually 1-3 sentences) to maintain an interactive teacher-student discussion.
5. Avoid long blocks of text or unrequested explanations. If they want code or optimization, they will ask.
6. Format key values (like O(N), variables) clearly, but keep overall markdown/text light.
7. If the student asks for references, tutorials, video guidance, or links, you MUST output the special tag `[YOUTUBE_SEARCH: <topic>]` (replace `<topic>` with a relevant search term like `[YOUTUBE_SEARCH: binary exponentiation recursive geeksforgeeks]`) inside your response. The system will automatically fetch and display the real YouTube video cards for them. Also provide friendly text guidance."""


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
