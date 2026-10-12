"""Create a portable delivery archive without temporary dependencies or licensed reference imagery."""
import pathlib,zipfile
root=pathlib.Path(__file__).resolve().parents[1]
archive=root/'output/UChicago_HydePark_Delivery.zip'
files=[]
for p in root.rglob('*'):
 if not p.is_file():continue
 parts=p.relative_to(root).parts
 if parts[0] in ['node_modules','tmp','.git'] or '__pycache__' in parts:continue
 if p.suffix in ['.zip','.npz','.pyc']:continue
 if parts[0]=='sources' and p.suffix.lower() in ['.pdf','.png','.jpg','.jpeg']:continue
 files.append(p)
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(files):z.write(p,p.relative_to(root))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 assert 'index.html' in z.namelist() and 'output/UChicago_HydePark_Layered.3dm' in z.namelist()
print('Verified archive:',len(files),'files;',archive.stat().st_size,'bytes')
