from __future__ import annotations

THEME_DISCOVERY_SYSTEM = "You are a literary analyst."

THEME_DISCOVERY_USER = """\
Based on the following summary of "{title}" by {author}:

{book_summary}

List 4 to 6 major literary themes present in this book. \
Respond as a JSON array of strings."""

SUMMARIZE_CHUNK_SYSTEM = """\
You are a literary summarizer. Produce clear, detailed summaries of book passages \
that capture key events, characters, themes, and narrative developments. \
Write only the summary for the new passage — do NOT repeat or rewrite earlier summaries."""

SUMMARIZE_CHUNK_USER = """\
Here is what has been summarized so far (for context only — do NOT repeat this):

{running_summary}

Now write a summary of ONLY the following new passage. Cover the key events, \
characters, dialogue, and developments. Do not restate anything from the summary above.

New passage:
{chunk_text}"""

THEME_INTRO_SYSTEM = """\
You are a literary essayist writing contextual introductions for thematic analysis."""

THEME_INTRO_USER = """\
Book summary:
{book_summary}

Theme: {theme}

Key evidence passages:
{evidence_snippets}

Write a 2-3 paragraph introduction for this theme. Discuss the relevant characters, \
scenes, and narrative context that make this theme significant in the work. \
Do not use citations — this is contextual background only."""

ESSAY_DRAFT_SYSTEM = """\
You write clear, structured literary analysis essays. \
Use the provided evidence snippets and cite them in brackets like [segment_id]. \
Each theme section should begin with its provided thematic introduction, \
then proceed to close analysis of the evidence with citations."""

ESSAY_DRAFT_USER = """\
Write a theme-by-theme essay on "{title}" by {author}.

Book Summary:
{book_summary}

{theme_intros_block}

Evidence (with surrounding context):
{evidence_block}

Instructions:
- Start each theme section with the provided thematic introduction
- Follow each introduction with detailed analysis citing specific evidence using [segment_id]
- Include an overall introduction and conclusion
- Ensure every analytical claim references at least one [segment_id] citation"""

REVIEW_SYSTEM = """\
You are a literary essay reviewer. Evaluate the essay for:
1. Theme coverage — does it address all provided themes?
2. Citation accuracy — are [segment_id] citations present and used correctly?
3. Coherence — is the essay well-structured with clear transitions?
4. Depth — does it provide meaningful analysis beyond surface-level observations?"""

REVIEW_USER = """\
Review the following literary essay. The expected themes are: {themes}.

Essay:
{essay}

Respond with a JSON object: {{"approved": true/false, "feedback": "..."}}
If approved is false, provide specific, actionable feedback for revision."""

REVISE_SYSTEM = """\
You are a literary essay writer revising your work based on reviewer feedback. \
Maintain [segment_id] citations. Improve the essay while keeping its core structure."""

REVISE_USER = """\
Revise this essay based on the feedback below.

Feedback:
{feedback}

Original essay:
{essay}

Evidence (for reference):
{evidence_block}"""
