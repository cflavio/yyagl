'''This module binds abstract interval classes and actual implementation
classes (for the Dependency Inversion Principle).'''
from yyagl.lib.p3d.ivals import P3dSeq, P3dWait, P3dPosIval, P3dFunc


Seq = P3dSeq
Wait = P3dWait
PosIval = P3dPosIval
Func = P3dFunc
