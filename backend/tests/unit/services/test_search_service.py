from services.search_service import search_web


def test_search_web_builds_context_from_results(mocker):
    mocker.patch(
        "services.search_service.tavily.search",
        return_value={
            "results": [
                {"url": "https://example.com/a", "content": "First snippet."},
                {"url": "https://example.com/b", "content": "Second snippet."},
            ]
        },
    )

    result = search_web("EUR to TND exchange rate")

    assert result == (
        "Source: https://example.com/a\nContent: First snippet.\n\n"
        "Source: https://example.com/b\nContent: Second snippet.\n\n"
    )


def test_search_web_passes_expected_search_params(mocker):
    spy = mocker.patch("services.search_service.tavily.search", return_value={"results": []})

    search_web("some query")

    spy.assert_called_once_with(query="some query", search_depth="advanced", max_results=5)


def test_search_web_returns_fallback_message_when_no_results(mocker):
    mocker.patch("services.search_service.tavily.search", return_value={"results": []})
    assert search_web("obscure query") == "No web results found."


def test_search_web_returns_failure_message_on_exception(mocker, capsys):
    mocker.patch(
        "services.search_service.tavily.search",
        side_effect=RuntimeError("Tavily API down"),
    )

    result = search_web("some query")

    assert result == "Web search failed."
    assert "Tavily Error: Tavily API down" in capsys.readouterr().out


def test_search_web_returns_failure_message_when_results_key_missing(mocker):
    mocker.patch("services.search_service.tavily.search", return_value={})
    assert search_web("query") == "Web search failed."