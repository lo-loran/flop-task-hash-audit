import hashlib,json,sys
from pathlib import Path
d=json.loads(Path(sys.argv[1]).read_text()); v=d["direct_rail_v1"]; t=v["task_hash"]; i=t["inputs"]; a=v["inputs"]
def pre(x): return b"FLOP/POUI/TASK\x01"+bytes.fromhex(x["genesis_hash_hex"])+bytes.fromhex(x["agent_account_id32_hex"])+int(x["nonce"]).to_bytes(8,"little")+bytes.fromhex(x["model_hash_hex"])+bytes.fromhex(x["payload_hash_hex"])+bytes.fromhex(x["commit_hash_hex"])
p=pre(i); h=hashlib.blake2b(p,digest_size=32).digest()
q=h+int(a["gn_weight"]).to_bytes(8,"little")+int(a["latency_ms"]).to_bytes(8,"little")+bytes.fromhex(a["model_hash_hex"])+bytes.fromhex(a["output_hash_hex"])+bytes.fromhex(a["decode_policy_hash_hex"])+bytes([a["tee_type"]["scale_tag"]])
checks=[("task preimage",p.hex()==t["preimage_hex"]),("task hash",h.hex()==t["hash_hex"]==a["task_hash_hex"]),("report preimage",q.hex()==v["report_data_preimage_hex"]),("report data",hashlib.sha256(q).digest()+bytes(32)==bytes.fromhex(v["report_data_hex"]))]
for k in ("genesis_hash_hex","agent_account_id32_hex","nonce","model_hash_hex","payload_hash_hex","commit_hash_hex"):
 x=i.copy()
 if k=="nonce": x[k]=str(int(x[k])+1)
 else: b=bytearray.fromhex(x[k]); b[0]^=1; x[k]=b.hex()
 checks.append(("mutation "+k,hashlib.blake2b(pre(x),digest_size=32).digest()!=h))
for n,ok in checks: print(("PASS" if ok else "FAIL")+" | "+n)
print("RESULTAT:", "PASS" if all(ok for _,ok in checks) else "FAIL")
sys.exit(0 if all(ok for _,ok in checks) else 1)
