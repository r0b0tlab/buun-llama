import importlib.util
import unittest
from pathlib import Path

PATH=Path(__file__).resolve().parents[1]/'scripts'/'serving_probe.py'

class ProbeTests(unittest.TestCase):
    def test_aggregate_uses_actual_tokens_and_elapsed(self):
        self.assertTrue(PATH.exists(), 'serving probe is missing')
        spec=importlib.util.spec_from_file_location('serving_probe',PATH)
        assert spec is not None and spec.loader is not None
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        result=mod.summarize([{'new_tokens':100,'wall_s':2,'ttft_s':.1,'decode_tps':60,'accepted':60,'proposed':80}, {'new_tokens':50,'wall_s':2,'ttft_s':.3,'decode_tps':30,'accepted':20,'proposed':40}])
        self.assertEqual(result['aggregate_tps'],37.5)
        self.assertEqual(result['n'],2)
        self.assertAlmostEqual(result['accepted_fraction'],2/3)
        self.assertAlmostEqual(result['median_ttft_s'],.2)

    def test_sse_parses_tokens_and_final_timing_without_done(self):
        spec=importlib.util.spec_from_file_location('serving_probe',PATH)
        assert spec is not None and spec.loader is not None
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        self.assertTrue(hasattr(mod,'events'), 'SSE parser is missing')
        lines=[b': keepalive\n',b'\n',b'data: {"content":"hello"}\n',b'\n',b'data: {"stop":true,"timings":{"predicted_n":1}}\n',b'data: [DONE]\n']
        got=list(mod.events(lines))
        self.assertEqual(len(got),2)
        self.assertEqual(got[-1]['timings']['predicted_n'],1)
        with self.assertRaises(ValueError):
            list(mod.events([b'data: {"error":{"message":"OOM"}}\n']))

    def test_measure_reads_stream_usage_and_content(self):
        import threading
        from http.server import BaseHTTPRequestHandler, HTTPServer
        spec=importlib.util.spec_from_file_location('serving_probe',PATH)
        assert spec is not None and spec.loader is not None
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        self.assertTrue(hasattr(mod,'measure'), 'stream measurement missing')
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,format,*args):pass
            def do_POST(self):
                self.rfile.read(int(self.headers['Content-Length']))
                self.send_response(200);self.end_headers()
                self.wfile.write(b'data: {"content":"answer"}\n\ndata: {"stop":true,"stop_type":"eos","timings":{"predicted_n":5,"predicted_per_second":50,"draft_n":6,"draft_n_accepted":3}}\n\n')
        server=HTTPServer(('127.0.0.1',0),Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            row=mod.measure('http://127.0.0.1:'+str(server.server_port),'hello',16,False)
            self.assertEqual(row['new_tokens'],5)
            self.assertEqual(row['content'],'answer')
            self.assertEqual(row['accepted'],3)
            self.assertGreaterEqual(row['wall_s'],row['ttft_s'])
        finally:
            server.shutdown();server.server_close();thread.join()

    def test_cli_help_exposes_reproducible_probe(self):
        import subprocess,sys
        result=subprocess.run([sys.executable,str(PATH),'--help'],capture_output=True,text=True,check=True)
        self.assertIn('--json-out',result.stdout)
        self.assertIn('--base-url',result.stdout)
        self.assertIn('server default',result.stdout)

if __name__=='__main__':unittest.main()
