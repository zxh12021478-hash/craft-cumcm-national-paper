"""New-input receiver check. Review generated receiver.py before executing this."""
from pathlib import Path
import importlib.util,itertools,json,math,random,inspect,hashlib,sys
P=Path(__file__).resolve().parent

def reference_predictions(X, models, classes):
    answers=[]
    for x in X:
        votes={c:0 for c in classes}
        for m in models:
            first,second=m['classes'];score=sum(w*v for w,v in zip(m['w'],x))+m['bias']
            vote=second if score>0 else first if score<0 else min(first,second)
            votes[vote]+=1
        answers.append(min(classes,key=lambda c:(-votes[c],c)))
    return answers

def main():
    path=Path(sys.argv[1]) if len(sys.argv)>1 else P/'receiver-after.py'
    spec=importlib.util.spec_from_file_location('received_startup',path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    rng=random.Random(20261031)
    gaps=[];sizes=[]
    for m,p,n in [(3,2,4),(2,4,3),(4,3,5),(1,1,2)]:
        H=[[rng.randint(-5,5)/3 for _ in range(p)] for _ in range(m)]
        r=[rng.randint(-5,5)/2 for _ in range(m)]
        L=[rng.randint(-3,3)/2 for _ in range(p)]
        D=[[rng.randint(-4,4)/5 for _ in range(n)] for _ in range(p)]
        encoded=mod.least_squares_qubo(H,r,L,D);Q=encoded['Q'];off=encoded['offset']
        assert len(Q)==n and all(len(row)==n for row in Q)
        assert max(abs(Q[i][j]-Q[j][i]) for i in range(n) for j in range(n))<1e-10
        local=[]
        for b in itertools.product((0,1),repeat=n):
            theta=[L[i]+sum(D[i][j]*b[j] for j in range(n)) for i in range(p)]
            direct=sum((sum(H[i][j]*theta[j] for j in range(p))-r[i])**2 for i in range(m))
            energy=sum(Q[i][j]*b[i]*b[j] for i in range(n) for j in range(n))+off
            local.append(abs(direct-energy))
            assert math.isclose(direct,energy,rel_tol=1e-11,abs_tol=1e-10),(m,p,n,b,direct,energy)
        gaps.extend(local);sizes.append({'rows':m,'parameters':p,'bits':n,'assignments':2**n,'max_abs_error':max(local)})
    X=[[i,j] for i,j in itertools.product((-1,0,1),repeat=2)]
    predictions=[]
    for case in range(8):
        models=[{'classes':[a,b],'w':[rng.randint(-3,3),rng.randint(-3,3)],'bias':rng.randint(-1,1)} for a,b in [(0,1),(0,2),(1,2)]]
        for classes in [[0,1,2],[2,0,1]]:
            expected=reference_predictions(X,models,classes)
            actual=mod.predict_ovo(X,models,classes)
            assert actual==expected,(case,classes,actual,expected)
            reverse=mod.predict_ovo(X,list(reversed(models)),classes)
            assert reverse==expected
            flipped=[dict(m,classes=list(reversed(m['classes'])),w=[-v for v in m['w']],bias=-m['bias']) for m in models]
            assert mod.predict_ovo(X,flipped,classes)==expected
            predictions.extend(actual)
    models=[{'classes':[0,1],'w':[0],'bias':1},{'classes':[0,2],'w':[0],'bias':-1},{'classes':[1,2],'w':[0],'bias':-1}]
    before=mod.predict_ovo([[0]],models,[0,1,2]);assert before==[1]
    models[2]['bias']=1
    after=mod.predict_ovo([[0]],models,[0,1,2]);assert after==[0]
    assert list(inspect.signature(mod.predict_ovo).parameters)==['X','models','classes']
    out={'status':'pass','receiver_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'qubo_cases':sizes,'total_assignments':len(gaps),'maximum_qubo_gap':max(gaps),'OVO_reference_evaluations':len(predictions),'OVO_distinct_model_point_cases':72,'pair_orientation_and_sign_consistency_checked':True,'OVO_model_order_and_class_order_checked':True,'third_pair_decisive':{'before':before,'after':after},'prediction_signature':'X,models,classes only','scope':'Independent direct arithmetic and prediction reference on AST-equivalent extracts of NEW received implementation. Exposed same-conversation regression, not blind or original solver/SDK/model-performance validation.'}
    raw_spec=importlib.util.spec_from_file_location('raw_receiver',P/'receiver-before.py')
    raw=importlib.util.module_from_spec(raw_spec);raw_spec.loader.exec_module(raw)
    failures=[]
    for name,biases in [('zero_pair_scores',[0,0,0]),('three_way_vote_tie',[1,-1,1])]:
        models=[{'classes':list(pair),'w':[0],'bias':bias} for pair,bias in zip([(0,1),(0,2),(1,2)],biases)]
        old=raw.predict_ovo([[0]],models,[2,0,1]);new=mod.predict_ovo([[0]],models,[2,0,1])
        assert old==[2] and new==[0]
        failures.append({'case':name,'expected':[0],'original':old,'repaired':new})
    out['original_failure_reproduced_and_repaired']=failures
    print(json.dumps(out,indent=2))

if __name__=='__main__': main()
