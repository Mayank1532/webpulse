"""Tests for deterministic HTML content extraction."""

from pydantic import HttpUrl

from webpulse.acquisition.document_models import WebDocument
from webpulse.acquisition.html_extractor import HTMLExtractor

URL = HttpUrl("https://example.com/article")


def test_extracts_title_and_body_text() -> None:
    html = """
    <html>
        <head>
            <title>WEBPULSE Test Page</title>
        </head>
        <body>
            <main>
                <h1>Live Web Intelligence</h1>
                <p>This is useful page content.</p>
            </main>
        </body>
    </html>
    """

    document = HTMLExtractor().extract(
        url=URL,
        html=html,
        content_type="text/html",
    )

    assert isinstance(document, WebDocument)
    assert document.title == "WEBPULSE Test Page"
    assert "Live Web Intelligence" in document.text
    assert "This is useful page content." in document.text
    assert document.content_type == "text/html"
    assert document.usable is True


def test_removes_script_and_style_content() -> None:
    html = """
    <html>
        <head>
            <title>Clean Page</title>
            <style>
                .secret { display: none; }
            </style>
            <script>
                const secret = "do-not-extract";
            </script>
        </head>
        <body>
            <p>Visible content.</p>
        </body>
    </html>
    """

    document = HTMLExtractor().extract(
        url=URL,
        html=html,
    )

    assert document.title == "Clean Page"
    assert document.text == "Clean Page Visible content."
    assert "do-not-extract" not in document.text
    assert "display: none" not in document.text


def test_removes_navigation_and_layout_noise() -> None:
    html = """
    <html>
        <head>
            <title>Article</title>
        </head>
        <body>
            <header>Site Header</header>
            <nav>Home Products Contact</nav>
            <main>
                <article>
                    <h1>Main Article</h1>
                    <p>Important information.</p>
                </article>
            </main>
            <aside>Related Links</aside>
            <footer>Copyright 2026</footer>
        </body>
    </html>
    """

    document = HTMLExtractor().extract(
        url=URL,
        html=html,
    )

    assert document.text == "Article Main Article Important information."
    assert "Site Header" not in document.text
    assert "Home Products Contact" not in document.text
    assert "Related Links" not in document.text
    assert "Copyright 2026" not in document.text


def test_removes_form_and_svg_content() -> None:
    html = """
    <html>
        <body>
            <form>
                Search Login Submit
            </form>

            <svg>
                Decorative SVG content
            </svg>

            <main>
                <p>Actual article text.</p>
            </main>
        </body>
    </html>
    """

    document = HTMLExtractor().extract(
        url=URL,
        html=html,
    )

    assert document.text == "Actual article text."
    assert "Search Login Submit" not in document.text
    assert "Decorative SVG content" not in document.text


def test_normalizes_whitespace() -> None:
    html = """
    <html>
        <body>
            <p>
                First
                line
            </p>

            <p>
                Second     line
            </p>
        </body>
    </html>
    """

    document = HTMLExtractor().extract(
        url=URL,
        html=html,
    )

    assert document.text == "First line Second line"


def test_missing_title_returns_empty_title() -> None:
    html = """
    <html>
        <body>
            <main>
                <p>Content without a title.</p>
            </main>
        </body>
    </html>
    """

    document = HTMLExtractor().extract(
        url=URL,
        html=html,
    )

    assert document.title == ""
    assert document.text == "Content without a title."
    assert document.usable is True


def test_empty_html_produces_unusable_document() -> None:
    document = HTMLExtractor().extract(
        url=URL,
        html="",
    )

    assert document.title == ""
    assert document.text == ""
    assert document.usable is False


def test_only_noise_produces_unusable_document() -> None:
    html = """
    <html>
        <body>
            <nav>Navigation</nav>
            <footer>Footer</footer>
            <script>ignored()</script>
            <style>ignored { color: red; }</style>
        </body>
    </html>
    """

    document = HTMLExtractor().extract(
        url=URL,
        html=html,
    )

    assert document.title == ""
    assert document.text == ""
    assert document.usable is False


def test_preserves_content_type_metadata() -> None:
    html = """
    <html>
        <head>
            <title>Metadata Test</title>
        </head>
        <body>
            <p>Content.</p>
        </body>
    </html>
    """

    document = HTMLExtractor().extract(
        url=URL,
        html=html,
        content_type="text/html; charset=utf-8",
    )

    assert document.content_type == "text/html; charset=utf-8"


def test_extraction_is_deterministic() -> None:
    html = """
    <html>
        <head>
            <title>Deterministic Page</title>
        </head>
        <body>
            <main>
                <h1>WEBPULSE</h1>
                <p>Same input should produce the same output.</p>
            </main>
        </body>
    </html>
    """

    extractor = HTMLExtractor()

    first = extractor.extract(
        url=URL,
        html=html,
    )

    second = extractor.extract(
        url=URL,
        html=html,
    )

    assert first == second
