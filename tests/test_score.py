import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).parents[1] / "src"
sys.path.insert(0, str(SRC))

SPEC = importlib.util.spec_from_file_location("score", SRC / "04_score.py")
assert SPEC is not None and SPEC.loader is not None
score = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(score)

PASSAGES = [
    {"passage_id": "a", "text": "Synthetic passage one."},
    {"passage_id": "b", "text": "Synthetic passage two."},
]


class FakeModel:
    def __init__(self, content='{"claim_status": "2", "rationale": "target"}'):
        self.content = content
        self.prompts = []

    def __call__(self, model, prompt, temperature, seed):
        self.prompts.append(prompt)
        return self.content, {"prompt_tokens": 10, "completion_tokens": 3}


class ParseLabelTests(unittest.TestCase):
    def test_valid_json_and_fenced_json(self):
        self.assertEqual(
            score.parse_label('{"claim_status": "3", "rationale": "r"}'), ("3", "r")
        )
        self.assertEqual(
            score.parse_label('```json\n{"claim_status": "u", "rationale": "r"}\n```')[0],
            "U",
        )

    def test_unknown_or_malformed_labels_are_invalid(self):
        self.assertEqual(score.parse_label('{"claim_status": "4"}')[0], score.INVALID)
        self.assertEqual(score.parse_label("not json")[0], score.INVALID)
        self.assertEqual(score.parse_label("[1, 2]")[0], score.INVALID)


class ScoreLlmTests(unittest.TestCase):
    def test_second_run_uses_cache_and_keeps_token_counts(self):
        with tempfile.TemporaryDirectory() as cache:
            model = FakeModel()
            rows, first = score.score_llm(PASSAGES, "Code: {passage}", "m", model, Path(cache))
            _, second = score.score_llm(PASSAGES, "Code: {passage}", "m", model, Path(cache))

        self.assertEqual([r["label"] for r in rows], ["2", "2"])
        self.assertEqual(model.prompts[0], "Code: Synthetic passage one.")
        self.assertEqual((first["calls"], first["cache_hits"]), (2, 0))
        self.assertEqual((second["calls"], second["cache_hits"]), (0, 2))
        self.assertEqual(second["prompt_tokens"], first["prompt_tokens"])

    def test_changing_prompt_or_model_misses_cache(self):
        with tempfile.TemporaryDirectory() as cache:
            model = FakeModel()
            score.score_llm(PASSAGES[:1], "v1 {passage}", "m", model, Path(cache))
            score.score_llm(PASSAGES[:1], "v2 {passage}", "m", model, Path(cache))
            score.score_llm(PASSAGES[:1], "v1 {passage}", "other", model, Path(cache))
        self.assertEqual(len(model.prompts), 3)


class OpenAICompatibleCallTests(unittest.TestCase):
    def test_posts_chat_completion_and_reads_usage(self):
        import json
        import threading
        from http.server import BaseHTTPRequestHandler, HTTPServer

        received = {}

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                received["path"] = self.path
                received["auth"] = self.headers.get("Authorization")
                received["body"] = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                reply = json.dumps({
                    "choices": [{"message": {"content": '{"claim_status": "1"}'}}],
                    "usage": {"prompt_tokens": 7, "completion_tokens": 2},
                }).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(reply)

            def log_message(self, *args):
                pass

        server = HTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.handle_request, daemon=True).start()
        call = score.openai_compatible_call(f"http://127.0.0.1:{server.server_port}/v1", "key")
        content, usage = call("m", "prompt", 0.0, 42)
        server.server_close()

        self.assertEqual(received["path"], "/v1/chat/completions")
        self.assertEqual(received["auth"], "Bearer key")
        self.assertEqual(received["body"]["temperature"], 0.0)
        self.assertEqual(received["body"]["seed"], 42)
        self.assertEqual(content, '{"claim_status": "1"}')
        self.assertEqual(usage, {"prompt_tokens": 7, "completion_tokens": 2})


if __name__ == "__main__":
    unittest.main()
