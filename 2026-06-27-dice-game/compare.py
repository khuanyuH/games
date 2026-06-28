import sys, random
sys.setrecursionlimit(10_000_000)
FACES=[1,2,3,4,5,6]
SUM=[sum(v for i,v in enumerate(FACES) if m>>i&1) for m in range(64)]

# ---- single-turn EV-optimal stopping policy (score-blind) ----
ev={}
def vev(mask):
    if mask in ev: return ev[mask]
    s=SUM[mask]
    rollev=sum((0.0 if mask&(1<<i) else vev(mask|(1<<i))) for i in range(6))/6.0
    v=max(s,rollev); ev[mask]=v; return v
def ev_bank(mask):  # True=bank
    if mask==0: return False
    s=SUM[mask]; rollev=sum((0.0 if mask&(1<<i) else vev(mask|(1<<i))) for i in range(6))/6.0
    return s>=rollev

# ---- generic solver: seats can be 'opt' or 'ev' ----
def build(seatA, seatB):
    vs={}; vd={}
    def term(d): return 1.0 if d>0 else (0.5 if d==0 else 0.0)
    def vstart(t,d):
        if t==6: return term(d)
        k=(t,d)
        if k in vs: return vs[k]
        v=sum(vdec(t,d,1<<i) for i in range(6))/6.0
        vs[k]=v; return v
    def vdec(t,d,mask):
        k=(t,d,mask)
        if k in vd: return vd[k]
        activeA=(t%2==0); seat=seatA if activeA else seatB; s=SUM[mask]
        bank = vstart(t+1, d+s) if activeA else vstart(t+1, d-s)
        roll=sum((vstart(t+1,d) if mask&(1<<i) else vdec(t,d,mask|(1<<i)))/6.0 for i in range(6))
        if seat=='ev':
            v = bank if ev_bank(mask) else roll
        else:
            v = max(bank,roll) if activeA else min(bank,roll)
        vd[k]=v; return v
    return vstart(0,0)

print("A value (win+0.5tie) by matchup [A_seat vs B_seat]:")
for sa in ('opt','ev'):
    for sb in ('opt','ev'):
        print(f"  A={sa:3s} B={sb:3s}: {build(sa,sb):.4f}")

# ---- independent Monte Carlo check of optimal-vs-optimal using DP action choice ----
# rebuild optimal value oracle
vs2={}; vd2={}
def term(d): return 1.0 if d>0 else (0.5 if d==0 else 0.0)
def vstart(t,d):
    if t==6: return term(d)
    k=(t,d)
    if k in vs2: return vs2[k]
    v=sum(vdec(t,d,1<<i) for i in range(6))/6.0; vs2[k]=v; return v
def vdec(t,d,mask):
    k=(t,d,mask)
    if k in vd2: return vd2[k]
    activeA=(t%2==0); s=SUM[mask]
    bank=vstart(t+1,d+s) if activeA else vstart(t+1,d-s)
    roll=sum((vstart(t+1,d) if mask&(1<<i) else vdec(t,d,mask|(1<<i)))/6.0 for i in range(6))
    v=max(bank,roll) if activeA else min(bank,roll); vd2[k]=v; return v
vstart(0,0)
def opt_bank(t,d,mask):
    activeA=(t%2==0); s=SUM[mask]
    bank=vstart(t+1,d+s) if activeA else vstart(t+1,d-s)
    roll=sum((vstart(t+1,d) if mask&(1<<i) else vdec(t,d,mask|(1<<i)))/6.0 for i in range(6))
    return (bank>=roll) if activeA else (bank<=roll)

def play_game(rng):
    d=0
    for t in range(6):
        activeA=(t%2==0); mask=0; s=0
        # forced first roll
        while True:
            if mask!=0 and opt_bank(t,d,mask):
                d += s if activeA else -s; break
            v=rng.randint(1,6); bit=1<<(v-1)
            if mask&bit:  # bust
                break
            mask|=bit; s=SUM[mask]
    return 1 if d>0 else (0 if d==0 else -1)
rng=random.Random(42); N=300000; w=t0=l=0
for _ in range(N):
    r=play_game(rng)
    if r>0: w+=1
    elif r==0: t0+=1
    else: l+=1
print(f"\nMonte Carlo opt-vs-opt (N={N}): A win {w/N:.3f}  tie {t0/N:.3f}  B win {l/N:.3f}")
print("(DP predicted: A 0.3946 tie 0.0361 B 0.5694)")
