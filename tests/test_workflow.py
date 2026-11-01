import copy,json,sys,unittest,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from editorial import validate_article,digest,check_approval,transition,release_payload,meta_payload
ROOT=Path(__file__).resolve().parents[1]
from fixtures import fixture
class EditorialTests(unittest.TestCase):
    def setUp(self):self.a=fixture()
    def test_complete_dry_run(self):
        a=copy.deepcopy(self.a);a['status']='proposed';a['verified']=True
        for stage in ['selected','writing','review']:a=transition(a,stage)
        approval={'approved_by':'TEST FIXTURE ONLY','evidence':'Simulation de test — aucune autorisation réelle','digest':digest(a)}
        a=transition(a,'approved',approval);a=transition(a,'published');self.assertEqual(release_payload(a)['mode'],'reviewed-export-only')
        a['approvals']['instagram']=approval
        payload=meta_payload(a,[f'https://example.test/slide-{i}.jpg' for i in range(5)])
        self.assertFalse(payload['publish']);self.assertEqual(len(payload['children']),5)
    def test_no_publication_without_approval(self):
        with self.assertRaises(ValueError):release_payload(self.a)
    def test_changed_content_revokes_approval(self):
        a=copy.deepcopy(self.a);a['verified']=True;a['approvals']={'site':{'approved_by':'TEST','evidence':'TEST','digest':digest(a)}};a['title']='Contenu modifié'
        with self.assertRaises(ValueError):check_approval(a)
    def test_instagram_needs_separate_approval(self):
        a=copy.deepcopy(self.a);a['verified']=True;a['approvals']={'site':{'approved_by':'TEST','evidence':'TEST','digest':digest(a)}}
        with self.assertRaises(ValueError):meta_payload(a,['https://example.test/a.jpg']*5)
    def test_unsafe_source_and_invalid_carousel_rejected(self):
        for change in ['source','carousel','slug']:
            a=copy.deepcopy(self.a)
            if change=='source':a['sources']=[{'url':'javascript:alert(1)','date':'2026-10-31','title':'unsafe'}]
            elif change=='carousel':a['instagram']['slides']=a['instagram']['slides'][:2]
            else:a['slug']='../../escape'
            with self.assertRaises(ValueError):validate_article(a)
    def test_reference_facts_and_catalogue_preserved(self):
        data=json.loads((ROOT/'content/catalogue.json').read_text());self.assertEqual(len(data),17)
        refs=json.loads((ROOT/'content/references.json').read_text());self.assertEqual(len(refs[0]['photos']),6);self.assertEqual(refs[1]['date'],'2026-10-24');self.assertNotIn('pending_photos',refs[1]);self.assertEqual(len(refs[1]['photos']),8)
if __name__=='__main__':unittest.main()
