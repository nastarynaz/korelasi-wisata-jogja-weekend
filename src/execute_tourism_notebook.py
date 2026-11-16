import nbformat,json,shutil
from pathlib import Path
from nbclient import NotebookClient
n=nbformat.read('COLAB_RUN.ipynb',as_version=4)
NotebookClient(n,timeout=240,kernel_name='python3',resources={'metadata':{'path':str(Path.cwd())}}).execute()
nbformat.write(n,'COLAB_RUN.ipynb')
images=sum('image/png' in o.get('data',{}) for c in n.cells if c.cell_type=='code' for o in c.outputs)
print('Charts:',images)
for c in n.cells:
 if c.cell_type=='code':
  for o in c.outputs:
   if o.output_type=='stream':print(o.text[-2500:])
# Copy the computed artifacts using the printed results path.
for o in n.cells[2].outputs:
 if o.output_type=='stream' and 'Hasil disimpan di' in o.text:
  root=Path(o.text.split('Hasil disimpan di',1)[1].strip())
  shutil.copytree(root,'outputs/tourism',dirs_exist_ok=True)
assert images==10
