from typing import List

ISSUE_SUMMARY_PROMPT = """
You are a remediation planning assistant. A GitHub issue was opened with the following title and body:

Title: {title}
Body:
{body}

Summarize the issue, identify the likely bug or enhancement, and list the most relevant file types or paths to inspect.
"""

RESEARCH_PROMPT = """
You are a research agent. Search for the best remediation references for this issue:

Issue summary:
{summary}

Provide short notes, relevant documentation, links, and a concrete recommendation for what to fix.
"""

PATCH_PROMPT = """
You are a code patch assistant. Given the repository summary, code search findings, and issue details, propose a minimal fix.

Repository summary:
{repo_summary}

Relevant files:
{relevant_files}

Issue text:
{issue_text}

Existing code search results:
{code_results}

Research references:
{research_notes}

Produce:
1) A short fix summary.
2) A list of file change notes, with each note containing:
   - path: <relative path>
   - reason: <short reason why this file was changed>
3) A dictionary mapping file paths to updated file contents.

Format the file change notes clearly so they can be parsed as plain text.
"""

VALIDATION_PROMPT = """
You are a validation assistant. Review the workflow result and describe whether the patch appears to address the issue, whether tests or lint pass, and any remaining risk.

Issue text:
{issue_text}

Patch summary:
{patch_summary}

Validation output:
{validation_output}

Reply with a short verification summary.
"""
