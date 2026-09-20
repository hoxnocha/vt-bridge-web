#!/usr/bin/env python3
"""Render the manuscript-grounded VT-Bridge architecture with Graphviz.

Requires Graphviz (dot); no Python packages or web runtime dependencies.
Run: python3 tools/render_method_diagrams.py [--dot /path/to/dot]
Graphical cells are schematic representations, not specified hidden dimensions.
Scientific source: VT-Bridge manuscript, Sections III-B/C and IV-D, and abstract.
Visual reference: RDP algorithm figure (https://reactive-diffusion-policy.github.io/).
The reference informs vector glyphs and module grouping; the architecture is VT-Bridge's.
"""
import argparse
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'diagrams'
BLUE = '#cddff3'
BLUE_EDGE = '#527caa'
ORANGE = '#f4dcc2'
ORANGE_EDGE = '#b38251'

def token_sequence(title, tokens, fill, border, note=''):
    cells = ''.join(f'<TD WIDTH="29" HEIGHT="27" BGCOLOR="{fill}" BORDER="1" COLOR="{border}"><FONT FACE="Times New Roman" POINT-SIZE="15">{t}</FONT></TD>' for t in tokens)
    return f'''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3">
      <TR><TD><B>{title}</B></TD></TR>
      <TR><TD><TABLE BORDER="0" CELLBORDER="0" CELLSPACING="3" CELLPADDING="3"><TR>{cells}</TR></TABLE></TD></TR>
      <TR><TD><FONT POINT-SIZE="12" COLOR="#596574">{note}</FONT></TD></TR></TABLE>>'''

def vector(symbol, colors, border, note=''):
    cells=''.join(f'<TD WIDTH="11" HEIGHT="32" BGCOLOR="{c}" BORDER="1" COLOR="{border}"></TD>' for c in colors)
    return f'''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3">
      <TR><TD><FONT FACE="Times New Roman" POINT-SIZE="18">{symbol}</FONT></TD></TR>
      <TR><TD PORT="vec"><TABLE BORDER="0" CELLBORDER="0" CELLSPACING="1" CELLPADDING="0"><TR>{cells}</TR></TABLE></TD></TR>
      <TR><TD><FONT POINT-SIZE="11" COLOR="#596574">{note}</FONT></TD></TR></TABLE>>'''

def source(mobile=False):
    direction = 'TB' if mobile else 'LR'
    common=f'''digraph VTBridge {{
  graph [rankdir={direction}, bgcolor="white", pad="0.15", nodesep="0.30", ranksep="0.33", splines=polyline, fontname="Helvetica", fontsize=16, compound=true];
  node [fontname="Helvetica", fontsize=15, fontcolor="#253344", color="#67788b", penwidth=1.25, margin="0.12,0.10"];
  edge [color="#64758a", penwidth=1.5, arrowsize=0.65, fontname="Helvetica", fontsize=12, fontcolor="#405267"];
  obs [shape=plain, label=<<TABLE BORDER="0" CELLBORDER="0" CELLPADDING="3"><TR><TD>Observation <FONT FACE="Times New Roman"><I>o</I></FONT></TD></TR><TR><TD>Instruction <FONT FACE="Times New Roman"><I>l</I></FONT></TD></TR></TABLE>>];
  vla [shape=box3d, style=filled, fillcolor="#e8edf3", label=<<B>Pretrained VLA</B><BR/><FONT FACE="Times New Roman" POINT-SIZE="22">π<SUP>VLA</SUP></FONT><BR/><FONT POINT-SIZE="12">Fine-tuned backbone</FONT>>];
  chunk [shape=plain, label={token_sequence('Action chunk A',['a<SUB>1</SUB>','a<SUB>2</SUB>','…','a<SUB>H</SUB>'],BLUE,BLUE_EDGE,'H = 50')}];
  force [shape=plain, label={token_sequence('Force window F',['f<SUB>t−n+1</SUB>','…','f<SUB>t</SUB>'],ORANGE,ORANGE_EDGE,'n = 50')}];
  subgraph cluster_adapter {{
    label=<<B>Residual adapter</B> <FONT FACE="Times New Roman">π<SUP>res</SUP></FONT><BR/><FONT POINT-SIZE="12">0.98M parameters · backbone-specific</FONT>>;
    labelloc=t; labeljust=l; color="#b8c4d0"; style="rounded,dashed"; penwidth=1.2; margin=18;
    action_encoder [shape=box3d, style=filled, fillcolor="{BLUE}", color="{BLUE_EDGE}", label=<<B>Transformer</B><BR/>Action encoder<BR/><FONT POINT-SIZE="11">Once per chunk</FONT>>];
    force_encoder [shape=box3d, style=filled, fillcolor="{ORANGE}", color="{ORANGE_EDGE}", label=<<B>Transformer</B><BR/>Force encoder<BR/><FONT POINT-SIZE="11">Each execution step</FONT>>];
    za [shape=plain, label={vector('z<SUP>a</SUP>',[BLUE]*3,BLUE_EDGE,'cached')}];
    zf [shape=plain, label={vector('z<SUB>t</SUB><SUP>f</SUP>',[ORANGE]*3,ORANGE_EDGE,'updated')}];
    fusion [shape=plain, label={vector('[zᵃ ; zᶠₜ]',[BLUE]*3+[ORANGE]*3,'#8490a0','Concatenate')}];
    mlp [shape=trapezium, orientation=90, style=filled, fillcolor="#ded9ee", color="#897da6", label=<<B>MLP</B><BR/><FONT POINT-SIZE="12">Residual<BR/>head</FONT>>];
    action_encoder:e -> za:w [color="{BLUE_EDGE}"];
    force_encoder:e -> zf:w [color="{ORANGE_EDGE}"];
    za:e -> fusion:w [color="{BLUE_EDGE}"];
    zf:e -> fusion:w [color="{ORANGE_EDGE}"];
    fusion:e -> mlp:w;
    {{rank=same; action_encoder; force_encoder;}}
    {{rank=same; za; zf;}}
  }}
  residual [shape=plain, label=<<FONT FACE="Times New Roman" POINT-SIZE="20">a<SUB>t</SUB><SUP>res</SUP></FONT>>];
  add [shape=circle, fixedsize=true, width=0.40, fontsize=22, label="+", margin=0];
  output [shape=plain, label=<<FONT FACE="Times New Roman" POINT-SIZE="20">a<SUB>t</SUB><SUP>exe</SUP></FONT><BR/><FONT POINT-SIZE="12">Robot command</FONT>>];
  obs -> vla;
  vla -> chunk;
  chunk -> action_encoder [color="{BLUE_EDGE}"];
  force -> force_encoder [color="{ORANGE_EDGE}"];
  mlp -> residual;
  residual -> add;
  add -> output;
'''
    if mobile:
        for old,new in [('action_encoder:e -> za:w','action_encoder:s -> za:n'),('force_encoder:e -> zf:w','force_encoder:s -> zf:n'),('za:e -> fusion:w','za:s -> fusion:n'),('zf:e -> fusion:w','zf:s -> fusion:n'),('fusion:e -> mlp:w','fusion:s -> mlp:n')]:
            common=common.replace(old,new)
        start=common.index('    label=<<B>Residual adapter')
        end=common.index('    action_encoder',start)
        common=common[:start]+'    label=""; color="#b8c4d0"; style="rounded,dashed"; penwidth=1.2; margin=18;\n'+common[end:]
        common+='''
  graph [labelloc=b, label="Dashed group: residual adapter (0.98M parameters)", fontsize=11];
  {rank=same; chunk; force;}
  nominal [shape=plain, label=<<FONT FACE="Times New Roman" POINT-SIZE="18">a<SUB>t</SUB></FONT><BR/><FONT POINT-SIZE="11">from A</FONT>>];
  {rank=same; nominal; add;}
  chunk:w -> nominal:w [constraint=false, color="#527caa", penwidth=1.8];
  nominal:e -> add:w [color="#527caa", penwidth=1.8];
'''
    else:
        common=common.replace('obs -> vla;', 'obs:s -> vla:n;').replace('vla -> chunk;', 'vla:s -> chunk:n;')
        common+='''
  {rank=same; obs; vla; chunk; force;}
  chunk -> force [style=invis];
  chunk:n -> add:n [constraint=false, minlen=5, color="#527caa", penwidth=1.8, xlabel=<<FONT FACE="Times New Roman" POINT-SIZE="17">a<SUB>t</SUB></FONT>>];
'''
    return common+'}\n'

def route_bypass(root, mobile):
    """Keep the outer residual connection clear of the encoder inputs.

    Graphviz lays out all modules. This final route uses their SVG coordinates
    because dot's unconstrained skip edge can otherwise cross the force branch.
    """
    ns = '{http://www.w3.org/2000/svg}'
    groups = {g.find(ns+'title').text: g for g in root.iter(ns+'g') if g.find(ns+'title') is not None}
    def points(value):
        values = [float(n) for n in re.findall(r'-?\d+(?:\.\d+)?', value)]
        return list(zip(values[::2], values[1::2]))
    chunk_points = [p for poly in groups['chunk'].findall(ns+'polygon') for p in points(poly.get('points'))]
    x0, x1 = min(x for x,y in chunk_points), max(x for x,y in chunk_points)
    cy = (min(y for x,y in chunk_points) + max(y for x,y in chunk_points))/2
    cluster = points(groups['cluster_adapter'].find(ns+'path').get('d'))
    if mobile:
        edge=groups['chunk:w->nominal:w']
        tx,ty=points(edge.find(ns+'polygon').get('points'))[1]
        background=points(groups['VTBridge'].find(ns+'polygon').get('points'))
        outer=max(min(x for x,y in background)+4, min(x0,min(x for x,y in cluster))-12)
        d=f'M{x0},{cy} H{outer} V{ty} H{tx-6}'
        arrow=f'{tx-7},{ty-2.5} {tx},{ty} {tx-7},{ty+2.5}'
    else:
        edge=groups['chunk:n->add:n']
        circle=groups['add'].find(ns+'ellipse')
        tx=float(circle.get('cx'));ty=float(circle.get('cy'))-float(circle.get('ry'))
        turn=(x1+min(x for x,y in cluster))/2
        top=min(y for x,y in cluster)-14
        d=f'M{x1},{cy} H{turn} V{top} H{tx} V{ty-6}'
        arrow=f'{tx-2.5},{ty-7} {tx},{ty} {tx+2.5},{ty-7}'
        labels=edge.findall(ns+'text')
        if labels:
            dx=(turn+tx)/2-float(labels[0].get('x'));dy=top-6-float(labels[0].get('y'))
            for t in labels:
                t.set('x',str(float(t.get('x'))+dx));t.set('y',str(float(t.get('y'))+dy))
    edge.find(ns+'path').set('d',d)
    edge.find(ns+'polygon').set('points',arrow)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dot',default='dot')
    args=parser.parse_args()
    OUT.mkdir(exist_ok=True)
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    for mobile in (False,True):
        name='vt-bridge-inference'+('-mobile' if mobile else '')
        gv=OUT/(name+'.gv');svg=OUT/(name+'.svg')
        gv.write_text('// Graphviz source generated by tools/render_method_diagrams.py\n'+source(mobile))
        subprocess.run([args.dot,'-Tsvg',str(gv),'-o',str(svg)],check=True)
        tree=ET.parse(svg);root=tree.getroot()
        root.set('role','img');root.set('aria-labelledby','architecture-title architecture-desc')
        title=ET.Element('{http://www.w3.org/2000/svg}title',{'id':'architecture-title'})
        title.text='VT-Bridge neural architecture'
        desc=ET.Element('{http://www.w3.org/2000/svg}desc',{'id':'architecture-desc'})
        desc.text='Two Transformer encoders map the VLA action chunk and recent force window to features. Their concatenation enters an MLP residual head. A skip connection adds the nominal action to the predicted residual. The action feature is cached; the force feature is updated at each execution step. Vector cells and module shapes are schematic, not layer counts or hidden dimensions.'
        root.insert(0,desc);root.insert(0,title)
        route_bypass(root,mobile)
        previous_script = None
        for t in root.iter('{http://www.w3.org/2000/svg}text'):
            if t.get('baseline-shift') and t.get('font-size'):
                size=float(t.get('font-size'))
                kind=t.get('baseline-shift')
                baseline=t.get('y')
                if kind=='super' and previous_script and previous_script[:2]==('sub',baseline):
                    t.set('x',previous_script[2])
                previous_script=(kind,baseline,t.get('x'))
                shift=-0.30*size if kind=='super' else 0.25*size
                t.set('y',str(round(float(t.get('y'))+shift,2)))
                t.set('font-size',str(round(size*0.65,2)))
                del t.attrib['baseline-shift']
            else:
                previous_script=None
        tree.write(svg,encoding='unicode',xml_declaration=True)
        print(name,root.get('viewBox'))

if __name__=='__main__': main()
