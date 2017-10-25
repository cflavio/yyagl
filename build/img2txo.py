from sys import argv
from os import remove, system

textured_egg = '''
<Material> Material {{ }}
<Texture> Tex {{ "{texture}" }}

  <Group> Cube {{
    <Transform> {{
      <Matrix4> {{
        1.0 0.0 0.0 0.0
        0.0 1.0 0.0 0.0
        0.0 0.0 1.0 0.0
        0.0 0.0 0.0 1.0
      }}
    }}

    <VertexPool> Cube {{

      <Vertex> 0 {{1.000000 0.999999 0.000000
        <UV> ORCO {{
          1.000000 1.000000
        }}
      }}
      <Vertex> 1 {{-1.000000 1.000000 0.000000
        <UV> ORCO {{
          0.000000 1.000000
        }}
      }}
      <Vertex> 2 {{-1.000000 -1.000000 0.000000
        <UV> ORCO {{
          0.000000 0.000000
        }}
      }}
      <Vertex> 3 {{0.999999 -1.000001 0.000000
        <UV> ORCO {{
          0.999999 0.000000
        }}
      }}}}


    <Polygon> {{
      <TRef> {{ Tex }}
      <MRef> {{ Material }}
      <Normal> {{0.000000 0.000000 1.000000}}
      <VertexRef> {{ 0 1 2 3 <Ref> {{ Cube }}}}
    }}
  }}'''

textured_egg = textured_egg.format(texture=argv[1])
nameid = argv[1].replace('/', '_')
dummyname = 'dummy_' + nameid
with open(dummyname + '.egg', 'w') as dummyegg: dummyegg.write(textured_egg)
system('egg2bam -txo -mipmap -ctex %s.egg -o %s.bam' % (dummyname, dummyname))
remove(dummyname + '.egg')
remove(dummyname + '.bam')
