## Plot band module

'''Band structure module: Functions of plotting the bands'''

from math import *
import cmath as cmt
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm
import matplotlib.colors
plt.rcParams['font.size']=18
plt.rcParams.update({'figure.autolayout': True})
from matplotlib.collections import LineCollection
from matplotlib.patches import Polygon
from mayavi import mlab

import sys
sys.path.append('../lattice')
import lattice as ltc
import brillouinzone as bz
sys.path.append('../tightbinding')
import tightbinding as tb
sys.path.append('../bandtheory')
import bandtheory as bdth




'''Plotting the bands'''


def mapfs(H,ks,nf,ltype,prds,Nk,datatype='e',sn=np.array([0.,0.,1.]),tosetde=False,de=0.):
    '''
    Obtain the Fermi surface for a given filling
    '''
    kps=[]
    data=[]
    Hks=np.array([H(k) for k in ks])
    ees,us=np.linalg.eigh(Hks)
    us=[u.conj().T for u in us]
    mu=bdth.fillingchempot(H,nf,ltype,prds,Nk)
    Nbd=np.shape(ees)[1]
    if(tosetde==False):de=100/Nk**2
    for n in range(Nbd):
        for nk in range(len(ks)):
            if(abs(ees[nk][n]-mu)<de):
                if(datatype=='f'):datak=0.5
                elif(datatype=='s'):
                    smat=0.5*np.kron(np.identity(round(np.shape(Hks[0])[0]/2)),np.tensordot(sn,np.array([tb.paulimat(n) for n in [1,2,3]]),(0,0)))
                    u=us[nk][n]
                    datak=np.linalg.multi_dot([u,smat,u.conj().T]).real
                kps+=[ks[nk]]
                data+=[datak]
    return kps,data


def mapband(H,nbd,ltype,prds,Nk,tosetde=False,de=0.):
    '''
    Obtain the Fermi surface for a given filling
    '''
    ks=bz.listbz(ltype,prds,Nk)[0]
    Hks=np.array([H(k) for k in ks])
    ees=list(np.linalg.eigvalsh(Hks).T[nbd])
    eeavg=sum(ees)/len(ees)
    ees=[10*(ee-eeavg) for ee in ees]
    dataks=[[ks[nk][0],ks[nk][1],ees[nk]] for nk in range(len(ks))]
    return dataks


def sectionband(H,mu,k1,k2,k0,Nk,datatype='e',sn=np.array([0.,0.,1.]),toend=True):
    '''
    Compute the band energies from the Hamiltonian H along a momentum-space line section k1-k2.
    '''
    # Momenta from k1 to k2.
    k12s=list(np.linspace(k1,k2,num=Nk,endpoint=toend))
    # Momentum resolution.
    dk=np.linalg.norm(k12s[1]-k12s[0])
    # List the momenta to draw: k0 is the starting point of the [k1,k2] section in the plot along the high-symmetry-point contour. 
    kscs=np.array([k0+nk*dk for nk in range(len(k12s))])
    # Obtain the band energies at all momenta in the [k1,k2] section.
    Hks=np.array([H(k) for k in k12s])
    datascs=[]
    if(datatype=='e'):
        eescs=np.linalg.eigvalsh(Hks).T
        datascs=eescs
    else:
        eescs,uscs=np.linalg.eigh(Hks)
        eescs=eescs.T
        uscs=[usc.conj().T for usc in uscs]
        if(datatype=='s'):
            smat=0.5*np.kron(np.identity(round(np.shape(Hks[0])[0]/2)),np.tensordot(sn,np.array([tb.paulimat(n) for n in [1,2,3]]),(0,0)))
            datascs=np.array([[np.linalg.multi_dot([u,smat,u.conj().T]).real for u in usc] for usc in uscs]).T
            for nk in range(len(kscs)):
                nb=0
                ndg=1
                while nb<len(eescs):
                    if(nb==len(eescs)-1 or abs(eescs[nb+1,nk]-eescs[nb,nk])>1e-12):
                        dataavg=sum([datascs[nb-n,nk] for n in range(ndg)])/ndg
                        for n in range(ndg):
                            datascs[nb-n,nk]=dataavg
                        ndg=1
                    else:ndg+=1
                    nb+=1
    return kscs,eescs,datascs


def plotbandcontour(H,ltype,prds,Nfl,Nk,nf=0.,eezm=1.,eezmmid=0.,zmkts=[0,-1],zmktszm=[1.,1.],datatype='e',sn=np.array([0.,0.,1.]),cttype='s',tosave=False,filetfig='',tobdg=False):
    '''
    Plot the band structure along a trajectory in the Brillouin zone.
    '''
    # Obtain the high-symmetry points.
    hsks=bz.hskcontour(ltype,prds,cttype)
    # Obtain the number of bands.
    Nbd=np.shape(H(hsks[0][1]))[0]
    # Determine the chemical potential mu that shows the filling. If no showing the filling, let nf=0 to plot all bands in blue.
    if(tobdg==False):mu=bdth.fillingchempot(H,nf,ltype,prds,Nk)
    elif(tobdg):mu=0.
    # Initial list of all plotted momenta.
    ks=np.array([])
    # Initial list of all plotted bands.
    bands=np.array([[] for n in range(Nbd)])
    # Initial list of all plotted band data.
    datas=np.array([[] for n in range(Nbd)])
    eemaxs,eemins=[],[]
    # Initial point of plotted momentum.
    k0=0.
    # Initial list of high-symmetry points kts and their labels ktlbs along the plotted contour. These are the ticks of the x axis.
    kts,ktlbs=[k0],[hsks[0][0]]
    for nsc in range(len(hsks)-1):
        # Exclude the end point except in the last segment.
        toend=(nsc==len(hsks)-2)
        # Obtain the momenta and band energies in the section.
        kscs,eescs,datascs=sectionband(H,mu,hsks[nsc][1],hsks[nsc+1][1],k0,Nk,datatype,sn,toend)
        # Add the momenta and band energies in the section to the overall lists.
        ks=np.concatenate((ks,kscs),axis=0)
        bands=np.concatenate((bands,eescs),axis=1)
        datas=np.concatenate((datas,datascs),axis=1)
        # Shift k0 to by the length of the [k1,k2] section.
        k0+=np.linalg.norm(hsks[nsc+1][1]-hsks[nsc][1])
        # Append the end momentum and its label to the list.
        kts+=[k0]
        ktlbs+=[hsks[nsc+1][0]]
        # Get the maximal and minimal values of the energy.
        eemaxs=eemaxs+[np.max(eescs)]
        eemins=eemins+[np.min(eescs)]
    # Determine the colors of the data.
    damax=max(0.001,np.max(abs(datas)))
    cmap=matplotlib.cm.get_cmap('coolwarm')
    norm=matplotlib.colors.Normalize(vmin=-damax,vmax=damax)
    def bandsegmentcolor(data0,data1,mu,datatype):
        # Determine the colors of a band segment [ee0,ee1].
        # Return green and blue below and above the chemical potential, respectively.
        if(datatype=='e'):
            if(data0<mu+1e-14 and data1<mu+1e-14):return 'g'
            else:return 'b'
        elif(datatype!='e'):
            if(abs(data0)>abs(data1)):datat=data0
            else:datat=data1
            return cmap(norm(datat))
    cs=[[bandsegmentcolor(datas[n,nk],datas[n,nk+1],mu,datatype) for nk in range(np.shape(bands)[1]-1)] for n in range(Nbd)]
    plt.rcParams.update({'font.size':30})
    for n in range(Nbd):
#        plt.scatter(ks,bands[n],s=2.,c=cs[n])
        # Obtain the collections of band segments.
        points=np.array([ks,bands[n]]).T.reshape(-1,1,2)
        segments=np.concatenate([points[:-1],points[1:]],axis=1)
        # Add the collection of band segments to the plot.
        lc=LineCollection(segments,colors=cs[n],linewidth=2)
        plt.gca().add_collection(lc)
        plt.gca().autoscale()
    # Set the ticks of the x axis as the high-symmetry points.
    [plt.axvline(x=hsk,color='k') for hsk in kts[1:-1]]
    plt.axhline(y=mu,color='k',linestyle='--')
    plt.xlim(kts[0],kts[-1])
    plt.xticks(ticks=kts,labels=ktlbs)
    # Set the y axis.
    plt.ylabel('$E_k$')
    # Zoom in.
    if(abs(eezm-1.)>1e-14):
        eemax,eemin=max(eemaxs),min(eemins)
        eediff=max(eemax-mu,mu-eemin)
        print('Zoom in to the Fermi surface by scale =',eezm)
        kts0,kts1=kts[zmkts[0]],kts[zmkts[1]]
        ktsmid,ktsdiff=(kts0+kts1)/2.,(kts1-kts0)/2.
        plt.xlim(ktsmid-zmktszm[0]*ktsdiff,ktsmid+zmktszm[1]*ktsdiff)
        plt.ylim(mu+eezmmid-(1./eezm)*eediff,mu+eezmmid+(1./eezm)*eediff)
        plt.axis('off')
    plt.gcf()
    if(tosave==True):plt.savefig(filetfig,dpi=2000,bbox_inches='tight',pad_inches=0,transparent=True)
    plt.show()


def plotbz(ltype,prds,ks,todata=False,data=[],ptype='pt',dks=[],bzop=False,toclmax=False,bzvol=1.,tolabel=False,tosave=False,filetfig=''):
    '''
    Draw the Brillouin zone.
    '''
    # Type of Brillouin zone.
    bztype=bz.typeofbz(ltype,prds)
    # All high-symmetry points of the Brillouin zone. Specifying 2D.
    hsks=[[kp[0],np.array([kp[1][0],kp[1][1]])] for kp in bz.hskpoints(ltype,prds)]
    # Rectangular Brillouin zone.
    if(bztype=='rc'):
        # Corners of the Brillouin zone.
        bzcs=[hsks[3][1],hsks[4][1],-hsks[3][1],-hsks[4][1],]
        # High-symmetry points to label.
        hskls=[hsks[0],hsks[1],hsks[2],hsks[3]]
    # Hexagonal Brillouin zone.
    elif(bztype=='hx'):
        # Corners of the Brillouin zone.
        bzcs=[hsks[4][1],-hsks[6][1],hsks[5][1],-hsks[4][1],hsks[6][1],-hsks[5][1],]
        # High-symmetry points to label.
        hskls=[hsks[0],hsks[1],[hsks[5][0],-hsks[5][1]]]
    # Draw the edges of the Brillouin zone.
    plg=Polygon(bzcs,facecolor='none',edgecolor='k',linewidth=3)
    plt.rcParams.update({'font.size':30})
    fig,ax=plt.subplots()
    ax.add_patch(plg)
    # High-symmetry points to label.
    if(tolabel):
        hsklxs,hsklys=[hsk[1][0] for hsk in hskls],[hsk[1][1] for hsk in hskls]
        hskltxs,hskltys=[1.1*hsk[1][0] for hsk in hskls],[1.1*hsk[1][1] for hsk in hskls]
        hskltxs[0]+=0.1*hskls[-1][1][0]
        hskltys[0]+=0.1*hskls[-1][1][1]
        [plt.text(hskltxs[n],hskltys[n],hskls[n][0]) for n in range(len(hskls))]
        plt.scatter(hsklxs,hsklys,c='r')
    # If there is data to present, map it out.
    if(todata):
        if(len(data)==0):data=len(ks)*[0.]
        if(ptype=='pt'):
            k0s,k1s,k2s=np.array(ks).T
            if(toclmax):camax=np.max(np.abs(np.array(data)))
            else:camax=max(np.max(np.abs(np.array(data))),1./bzvol)
            plt.scatter(k0s,k1s,s=40.,c=data,vmin=-camax,vmax=camax,cmap='coolwarm')
        elif(ptype=='gd'):
            kctss=[bz.gridcorners(k,dks) for k in ks]
            if(bzop==False):
                # All high-symmetry points of the Brillouin zone.
                hsks=bz.hskpoints(ltype,prds)
                # Number of side pairs.
                Nsdp=round((len(hsks)-1)/2)
                Nsft=2*(Nsdp-2)+1
                # Edge centers of the Brillouin zone.
                kecs=[hsks[nsdp+1][1] for nsdp in range(Nsdp)]
                for nkcts in range(len(kctss)):
                    kcts=kctss[nkcts]
                    kctst=[]
                    Nkct=len(kcts)
                    for nkct in range(Nkct):
                        if(bz.inbz(kcts[nkct],kecs,Nsdp,bzop=bzop)):kctst+=[kcts[nkct]]
                        elif(bz.inbz(kcts[nkct],kecs,Nsdp,bzop=bzop)==False):
                            if(bz.inbz(kcts[(nkct-Nsft)%Nkct],kecs,Nsdp,bzop=bzop)):kctst+=[(kcts[nkct]+kcts[(nkct-Nsft)%Nkct])/2.]
                            elif(bz.inbz(kcts[(nkct+Nsft)%Nkct],kecs,Nsdp,bzop=bzop)):kctst+=[(kcts[nkct]+kcts[(nkct+Nsft)%Nkct])/2.]
                            else:kctst+=[(kcts[nkct]+kcts[(nkct+Nsdp)%Nkct])/2.]
                    kctss[nkcts]=kctst
            kctss=[np.array(kcts)[:,0:2] for kcts in kctss]
            cmap=matplotlib.cm.get_cmap('coolwarm')
            if(toclmax):camax=np.max(np.abs(np.array(data)))
            else:camax=max(np.max(np.abs(np.array(data))),1./bzvol)
            norm=matplotlib.colors.Normalize(vmin=-camax,vmax=camax)
            cs=[cmap(norm(data[nk])) for nk in range(len(ks))]
            for nk in range(len(ks)):
                plgk=Polygon(kctss[nk],facecolor=cs[nk],edgecolor='None',linewidth=0)
                ax.add_patch(plgk)
            if(bzop==False):
                plg=Polygon(bzcs,facecolor='none',edgecolor='k',linewidth=3)
                ax.add_patch(plg)
    ax=plt.gca()
    lim=np.max(np.abs(np.array(bzcs)))*1.1
    ax.set_xlim([-lim,lim])
    ax.set_ylim([-lim,lim])
    ax.set_aspect('equal', adjustable='box')
    plt.axis('off')
    if(tosave):plt.savefig(filetfig,dpi=2000,bbox_inches='tight',pad_inches=0,transparent=True)
    plt.show()








