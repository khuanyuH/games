import sys
sys.setrecursionlimit(10_000_000)

FACES=[1,2,3,4,5,6]
SUM=[sum(v for i,v in enumerate(FACES) if m>>i&1) for m in range(64)]
POPC=[bin(m).count('1') for m in range(64)]

# ---------- Full-game optimal: value = first player (A) payoff, win=1 tie=.5 loss=0 ----------
# State reduced to (t, d, mask) where d = A_total - B_total (only the difference matters).
val_s={}  # start-of-turn values
val_d={}  # decision-node values

def terminal(d):
    return 1.0 if d>0 else (0.5 if d==0 else 0.0)

def vstart(t,d):
    if t==6: return terminal(d)
    key=(t,d)
    if key in val_s: return val_s[key]
    v=sum(vdec(t,d,1<<i) for i in range(6))/6.0   # forced first roll, never busts
    val_s[key]=v
    return v

def vdec(t,d,mask):
    key=(t,d,mask)
    if key in val_d: return val_d[key]
    activeA=(t%2==0)
    s=SUM[mask]
    bank = vstart(t+1, d+s) if activeA else vstart(t+1, d-s)
    roll=0.0
    for i in range(6):
        bit=1<<i
        roll += (vstart(t+1,d) if mask&bit else vdec(t,d,mask|bit))/6.0
    v = max(bank,roll) if activeA else min(bank,roll)
    val_d[key]=v
    return v

opt=vstart(0,0)

# ---------- Exact outcome distribution under optimal-vs-optimal ----------
dist_s={}; dist_d={}
def dstart(t,d):
    if t==6:
        return (1.0,0,0) if d>0 else ((0,1.0,0) if d==0 else (0,0,1.0))
    key=(t,d)
    if key in dist_s: return dist_s[key]
    w=ti=l=0.0
    for i in range(6):
        a,b,c=ddec(t,d,1<<i); w+=a/6; ti+=b/6; l+=c/6
    dist_s[key]=(w,ti,l); return (w,ti,l)
def ddec(t,d,mask):
    key=(t,d,mask)
    if key in dist_d: return dist_d[key]
    activeA=(t%2==0); s=SUM[mask]
    bankv = vstart(t+1,d+s) if activeA else vstart(t+1,d-s)
    rollv=0.0
    for i in range(6):
        bit=1<<i
        rollv += (vstart(t+1,d) if mask&bit else vdec(t,d,mask|bit))/6.0
    choose_bank = (bankv>=rollv) if activeA else (bankv<=rollv)  # active optimizes own
    if choose_bank:
        res=dstart(t+1, d+s if activeA else d-s)
    else:
        w=ti=l=0.0
        for i in range(6):
            bit=1<<i
            a,b,c = dstart(t+1,d) if mask&bit else ddec(t,d,mask|bit)
            w+=a/6; ti+=b/6; l+=c/6
        res=(w,ti,l)
    dist_d[key]=res; return res

W,T,L=dstart(0,0)
print(f"=== FULL-GAME OPTIMAL (both perfect) ===")
print(f"A (first player) value (win+0.5*tie): {opt:.4f}")
print(f"P(A win)={W:.4f}  P(tie)={T:.4f}  P(B win)={L:.4f}")
print(f"First-mover advantage: A wins {W:.3f} vs B {L:.3f}")
print(f"states: start={len(val_s)} decision={len(val_d)}")

# ---------- Single-turn EV-optimal stopping (ignores score) ----------
ev={}
def vev(mask):
    if mask in ev: return ev[mask]
    s=SUM[mask]; k=POPC[mask]
    rollev=sum((0.0 if mask&(1<<i) else vev(mask|(1<<i))) for i in range(6))/6.0
    v=max(s,rollev); ev[mask]=v; return v
# expected points per turn under EV-optimal:
ev_turn=sum(vev(1<<i) for i in range(6))/6.0
print(f"\n=== SINGLE-TURN EV-OPTIMAL STOPPING (score-blind) ===")
print(f"Expected points banked per turn: {ev_turn:.3f}")
# stopping rule: for each mask, bank iff sum>=rollEV
def bank_pref(mask):
    s=SUM[mask]; rollev=sum((0.0 if mask&(1<<i) else vev(mask|(1<<i))) for i in range(6))/6.0
    return s>=rollev
# summarize by number of distinct rolled k: min sum at which we bank
print("Stopping frontier (bank vs roll) by #distinct numbers held:")
for k in range(1,7):
    masks=[m for m in range(64) if POPC[m]==k]
    banked=[SUM[m] for m in masks if bank_pref(m)]
    rolled=[SUM[m] for m in masks if not bank_pref(m)]
    print(f"  k={k}: bust prob next={k/6:.2f} | BANK at sums {sorted(set(banked))} | ROLL on {sorted(set(rolled))}")
