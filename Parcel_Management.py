from collections import deque, defaultdict
import heapq
from datetime import datetime

db,dq,pq=[],deque(),[]
g=defaultdict(list)
S=["Registered","Picked Up","In Transit","Out for Delivery","Delivered"]

class P:
    def __init__(self,tid,s,r,o='',d='',dist=0,w=0):
        self.tid,self.sender,self.receiver=tid,s,r
        self.origin,self.destination,self.distance,self.weight=o,d,dist,w
        self.status="Registered"
        self.history=[("Registered",datetime.now().strftime("%Y-%m-%d %H:%M"))]
    def __str__(self):return f"[{self.tid}] {self.sender}→{self.receiver} | {self.status}"

def find(tid):
    for p in db:
        if p.tid==tid.upper():return p
    return None

def calc_pri(p):
    s=(100-min(float(p.weight or 0),100))*0.3
    sp={"Delivered":100,"Out for Delivery":80,"In Transit":60,"Picked Up":40,"Registered":20}
    s+=sp.get(p.status,20)*0.4
    age=(datetime.now()-datetime.strptime(p.history[0][1],"%Y-%m-%d %H:%M")).total_seconds()/3600
    s+=min(age*2,100)*0.3
    return -s

def dijkstra(s,e):
    s,e=s.lower(),e.lower()
    d={l:float('inf')for l in g}
    d[s],p,v=0,[(0,s,[s])],set()
    while p:
        dist,c,path=heapq.heappop(p)
        if c in v:continue
        v.add(c)
        if c==e:return dist,path
        for nb,w in g[c]:
            if nb not in v:
                nd=dist+w
                if nd<d[nb]:d[nb]=nd;heapq.heappush(p,(nd,nb,path+[nb]))
    return float('inf'),[]

def build_graph():
    g.clear()
    for p in db:
        o,d=p.origin.lower(),p.destination.lower()
        if o and d and p.distance>0:g[o].append((d,p.distance));g[d].append((o,p.distance))

def enqueue(tid):
    p=find(tid)
    if not p:print(f"Error: '{tid}' not found.");return False
    if p in dq:print(f"'{tid}' already in queue.");return False
    dq.append(p);print(f"✓ Queued: {p}");return True

def process():
    if not dq:print("Queue empty.");return None
    p=dq.popleft();i=S.index(p.status)
    if i<len(S)-1:
        p.status=S[i+1];p.history.append((p.status,datetime.now().strftime("%Y-%m-%d %H:%M")))
        if p.status!="Delivered":dq.append(p);print(f"→ {p.tid}: {p.status}")
        else:print(f"✓ {p.tid} delivered to {p.receiver}")
    return p

def update(tid,st):
    if st not in S:print(f"Invalid. Choose: {', '.join(S)}");return False
    p=find(tid)
    if not p:print(f"'{tid}' not found.");return False
    p.status=st;p.history.append((st,datetime.now().strftime("%Y-%m-%d %H:%M")))
    if st=="Delivered" and p in dq:dq.remove(p)
    print(f"✓ {tid} → {st}");return True

def add_pri(tid):
    p=find(tid)
    if not p:return False
    heapq.heappush(pq,(calc_pri(p),datetime.now().isoformat(),tid,p))
    print(f"✓ Priority queued: {tid}");return True

def proc_pri():
    if not pq:print("Priority queue empty.");return None
    s,ts,tid,p=heapq.heappop(pq);print(f"→ Priority: {tid} (score: {abs(s):.2f})");return p

def view_q():
    print(f"\n{'='*50}\nDELIVERY QUEUE ({len(dq)})\n{'='*50}")
    if not dq:print("Empty.");return
    for i,p in enumerate(dq,1):
        m=" ← NEXT"if i==1 else""
        print(f"\n#{i}{m}\n  {p.tid} | {p.sender}→{p.receiver}\n  Status: {p.status}")

def view_all():
    print(f"\n{'='*50}\nALL PARCELS ({len(db)})\n{'='*50}")
    for p in db:
        print(f"\n{p}")
        for st,ts in p.history:print(f"  {ts} → {st}")
    d=sum(1 for p in db if p.status=="Delivered")
    print(f"\nTotal: {len(db)} | Queue: {len(dq)} | Delivered: {d}")

def route(o,d):
    dist,path=dijkstra(o,d)
    if dist==float('inf'):return{"error":"No route"}
    return{"origin":o,"dest":d,"km":round(dist,2),"path":path,"hrs":round(dist/60,2)}

if __name__=="__main__":
    from Parcel_Registration import ParcelRegistration
    reg=ParcelRegistration()
    print("\nLoading sample data...")
    for s,r,o,d,w in[("Alice","Brian","Nairobi","Mombasa",10),("Carol","David","Kisumu","Eldoret",5),("Eve","Frank","Mombasa","Nairobi",15)]:
        p=reg.register_parcel(s,r,o,d,w)
        if p.get('tracking_number'):db.append(P(p['tracking_number'],s,r,o,d,w,w));dq.append(db[-1])
    build_graph()
    while True:
        print(f"\n{'='*50}\nPARCEL MANAGEMENT\n{'='*50}")
        print("1. Add Queue\n2. Process\n3. Update\n4. Delivered\n5. View Queue\n6. View All\n7. Priority\n8. Route\n9. Exit")
        c=input("\nChoice: ").strip()
        if c=="1":enqueue(input("ID: ").strip())
        elif c=="2":process()
        elif c=="3":update(input("ID: ").strip(),input(f"Status {S}: ").strip())
        elif c=="4":update(input("ID: ").strip(),"Delivered")
        elif c=="5":view_q()
        elif c=="6":view_all()
        elif c=="7":add_pri(input("ID: ").strip());proc_pri()
        elif c=="8":
            r=route(input("From: ").strip(),input("To: ").strip())
            if"error"in r:print(f"Error: {r['error']}")
            else:print(f"Route: {'→'.join(r['path'])}\nDist: {r['km']}km | {r['hrs']}h")
        elif c=="9":print("Exiting...");break
        else:print("Invalid!")