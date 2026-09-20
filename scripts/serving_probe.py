#!/usr/bin/env python3
"""Stdlib serving throughput probe. Never estimates generated tokens from caps."""
import statistics
import json
import time
import urllib.request

def measure(base,prompt,max_tokens=256,cache=False):
    body={'prompt':prompt,'n_predict':max_tokens,'temperature':0,'seed':42,'stream':True,'cache_prompt':cache}
    req=urllib.request.Request(base.rstrip('/')+'/completion',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
    start=time.perf_counter();first=None;content=[];final=None
    with urllib.request.urlopen(req,timeout=900) as response:
        for event in events(response):
            text=event.get('content','')
            if text:
                if first is None:first=time.perf_counter()-start
                content.append(text)
            if event.get('stop'):final=event
    wall=time.perf_counter()-start
    if final is None or first is None:raise ValueError('Missing final timings or generated text')
    t=final['timings'];new=t['predicted_n']
    if new<=0:raise ValueError('Zero generated tokens')
    return {'new_tokens':new,'wall_s':wall,'ttft_s':first,'decode_tps':t['predicted_per_second'],'accepted':t.get('draft_n_accepted',0),'proposed':t.get('draft_n',0),'content':''.join(content),'timings':t,'stop_type':final.get('stop_type')}

def events(lines):
    for raw in lines:
        line=raw.decode('utf-8').strip()
        if not line.startswith('data:'):continue
        value=line[5:].strip()
        if value=='[DONE]':break
        event=json.loads(value)
        if 'error' in event:raise ValueError(event['error'])
        yield event

def summarize(rows):
    if not rows:
        raise ValueError('No requests')
    if any(r['wall_s']<=0 or r['new_tokens']<=0 for r in rows):
        raise ValueError('Invalid request measurements')
    new=sum(r['new_tokens'] for r in rows)
    accepted=sum(r['accepted'] for r in rows)
    proposed=sum(r['proposed'] for r in rows)
    return {'n':len(rows),'tokens':new,'aggregate_tps':new/sum(r['wall_s'] for r in rows),'mean_tps':statistics.mean(r['new_tokens']/r['wall_s'] for r in rows),'median_ttft_s':statistics.median(r['ttft_s'] for r in rows),'median_decode_tps':statistics.median(r['decode_tps'] for r in rows),'accepted_fraction':accepted/proposed if proposed else None}

def main(argv=None):
    import argparse
    from pathlib import Path
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url',default='http://127.0.0.1:8888')
    parser.add_argument('--json-out',required=True)
    parser.add_argument('--reasoning-effort',choices=['low','medium','xhigh'],default=None,help='Override the server default; omitted preserves the profile.')
    parser.add_argument('--max-tokens',type=int,default=256)
    args=parser.parse_args(argv)
    source=Path(__file__).resolve().parents[1]/'eval/gsm8k_n40.jsonl'
    questions=[json.loads(line)['question'] for line in source.read_text().splitlines()][:2]
    questions += [
        'Write a Python LRU cache using collections.OrderedDict. Include get and put and a small example.',
        'Write a Python function that merges overlapping integer intervals, explain its complexity and give a test.',
        'Explain how a refrigerator transfers heat, including the compressor and expansion valve.',
        'Compare optimistic and pessimistic concurrency control in a database using one example.',
    ]
    def render(text):
        data={'messages':[{'role':'user','content':text}]}
        if args.reasoning_effort is not None:
            data['chat_template_kwargs']={'reasoning_effort':args.reasoning_effort}
        req=urllib.request.Request(args.base_url.rstrip('/')+'/apply-template',data=json.dumps(data).encode(),headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=60) as response:return json.load(response)['prompt']
    measure(args.base_url,render('Explain a prime number in one sentence.'),64,False)
    rows=[measure(args.base_url,render(q),args.max_tokens,False) for q in questions]
    output={'reasoning_effort':args.reasoning_effort,'max_tokens':args.max_tokens,'summary':summarize(rows),'rows':rows}
    path=Path(args.json_out);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output['summary'],indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
