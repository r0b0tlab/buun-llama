import json,os,shlex,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ProfileTests(unittest.TestCase):
    def test_profile_is_self_contained(self):
        path=ROOT/'recipes/dflash2-optimized.env'
        self.assertTrue(path.exists(),'optimized profile missing')
        command='source "$1"; python3 -c '+shlex.quote('import os,json; print(json.dumps(dict(os.environ)))')
        result=subprocess.run(['bash','-c',command,'profile',str(path)],capture_output=True,text=True,check=True,env={'PATH':os.environ['PATH']})
        env=json.loads(result.stdout)
        self.assertEqual(env['GGML_DFLASH2_BLOCK_SIZE_OVERRIDE'],'8')
        self.assertEqual(env['GGML_DFLASH_DRAFT_ADAPTIVE'],'1')
        fields=subprocess.check_output(['bash','-c','source "$1"; printf "%s\\n" "$CTX" "$UBATCH" "$N_PARALLEL" "$EXTRA_ARGS"','profile',str(path)],text=True).splitlines()
        self.assertEqual(fields[:3],['262144','512','1'])
        # serve.sh deliberately uses whitespace splitting, not eval/shlex.
        args=fields[3].split()
        self.assertEqual(json.loads(args[args.index('--chat-template-kwargs')+1]),{'reasoning_effort':'low'})
        self.assertEqual(args[args.index('--fit')+1],'off')
        self.assertIn('--no-vbr-prompt-cache',args)

if __name__=='__main__':unittest.main()
