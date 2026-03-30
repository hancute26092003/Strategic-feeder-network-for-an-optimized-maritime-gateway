/*********************************************
 * OPL 12.9.0.0 Model
 * Author: quynh
 * Creation Date: 28 thg 2, 2025 at 14:33:23
 *********************************************/
int numS = 4; 
range rangeS = 1..numS; 
int numM = 3;
range rangeM = 1..numM;
tuple Arc{ 
int Origin; 
int Destination; 
} 
{int} H = ...; 
{Arc} HArc=...; //mainline
{Arc} OD = ...; 
{int} OrgSet = ...; 
{int} DesSet = ...; 
{Arc} possarc1Set = {<o,d> | o in OrgSet, d in H: o != d}; 
{Arc} possarc2Set = {<d,d2> | d in H, d2 in DesSet : d != d2}; 
{Arc} PArc =  possarc1Set union HArc union possarc2Set;  
int Demand[OD] = ...; 
float FC[rangeS]= ...; //fixed cost of ship type s 
float FCM[rangeM] = ...; //fixed cost of ship for mainline
int t = ...; //transporting cost per distance 
int r = ...; //unit cost of each transshipment of a container 
float l[PArc]=...; //transportation distance from port i to port j 
int CapHub = ...; 
//Decision variable 
float Cap[rangeS]=...; //capacity of ship type s 
float CapM[rangeM] =...; //capacity of ship type in mainline
dvar boolean X[OD][rangeS][PArc];  
dvar boolean Z[OD][rangeS];  
dvar float+ q[H]; //quantity (number of containers) of vehicle in main route ship 
dvar float+ L[H]; //loading containers in main route ship 
dvar boolean Y[rangeM]; //binary variable limits vehicle used in main route must be one type 
dvar boolean U[rangeM]; //number of ship 
//*********************************************************************
dvar float+ arrival[H]; // arrival time of the ship in the main route 
float service[H]=...; //service time at main route set
float  travel[HArc]=...; // travelling time between main route set
dvar boolean n[HArc]; //binary check the main route available or not
//*********************************************************************
int F=...;
int C=...; //Number of available feeder ships at destination port 
range fromports=1..F; 
range toports=1..F;  
range ports=2..F; 
range ship = 1..C; 
float CapF=...; // 1 loaòi feeder
float D[fromports][toports]=...;//travelling distance
float DemandF[toports]=...; 
dvar boolean G[ship][fromports][toports]; 
dvar int+ u[ports]; //variables specifying the visiting order of port i in the main route to eliminate subtours
//***************************************************
dexpr float C1 = sum(s in rangeS, <o,d> in OD)(FC[s]*Z[<o,d>][s])+ sum(m in 
rangeM)(FCM[m]*U[m]); 
dexpr float C2 = sum(e in OD, s in rangeS,<i,j> in 
PArc)(t*l[<i,j>]*X[e][s][<i,j>])+sum(<i,j> in HArc)(t*l[<i,j>]); 
dexpr float C3 = sum(k in H)(r*L[k]); 
dexpr float C4 =  sum(i in fromports,j in toports, c in ship: i!=j) D[i][j]*G[c][i][j]*t;
dexpr float TC = C1 + C2 + C3 + C4; 
//Objective function 
execute SETTING{
//cplex.intSolLim=1;
}
minimize TC; 
subject to{ 
constraint1: 
forall (<o,d> in OD){ 
    sum (<o,k> in PArc, s in rangeS: k!= d) X[<o,d>][s][<o,k>] == 1; 
    sum (<k,d> in PArc, s in rangeS: k!= o) X[<o,d>][s][<k,d>] == 1; 
  }  
  constraint2: 
 forall (<o,d> in OD, s in rangeS){ 
    Z[<o,d>][s] == sum (<o,k> in PArc) X[<o,d>][s][<o,k>]; 
  } 
  constraint3: 
  forall (<o,d> in OD, s in rangeS) { 
    (Z[<o,d>][s] == 1) => (Demand[<o,d>] <= Cap[s]); 
  } 
  constraint4: 
  forall(k in H){ 
    sum(<o,d> in OD,s in rangeS)(sum(<o,k> in 
PArc)X[<o,d>][s][<o,k>]+sum(<k,d> in PArc)X[<o,d>][s][<k,d>]) <= CapHub; 
  }  
  constraint5: 
  forall (<k1,k2> in HArc){ 
    q[k2] == q[k1] + L[k2]; 
  } 
  constraint6: 
  	q[1000]==L[1000]; 
  	
  constraint7:
  forall(k in H){ 
  L[k] == sum(<o,d> in OD, s in rangeS)X[<o,d>][s][<o,k>] * Demand[<o,d>]; 
   }      
   constraint8: 
   sum(m in rangeM) Y[m]== 1;
   
   constraint9:                   
   forall(m in rangeM){ 
     Y[m]==0 =>U[m]==0; 
   } 
   constraint10: 
   forall (k in H){ 
     sum (m in rangeM)U[m]*CapM[m]>=q[k]; 
   }   
   constraint11:
   forall (<k1,k2> in HArc) { 
   	n[<k1,k2>] == 1; //main route always available 
   (n[<k1,k2>] == 1) => (arrival[k2] >= arrival[k1] + service[k1] + travel[<k1,k2>]); 
  } 
  	constraint12:    
     forall(j in toports:j!=1) 
       sum(i in fromports,c in ship:i!=j) G[c][i][j]==1; 
     constraint13:   
     forall(i in fromports:i!=1) 
       sum(j in toports,c in ship:j!=i) G[c][i][j]==1; 
     constraint14: 
     forall(i in fromports:i!=1)  
       sum(j in toports,c in ship:j!=i) G[c][1][j]<= C; 
     constraint15: 
     forall(j in toports:j!=1) 
       sum(i in fromports,c in ship: i!=j) G[c][i][1]<= C; 
     constraint16:   
     forall (i in fromports, j in  toports,c in ship) G[c][i][j]+G[c][j][i]<=1; 
     constraint17: 
     forall (c in ship) 
       sum(j in toports, i in fromports:i!=j && j!=1) DemandF[j]*G[c][i][j]<=CapF;     
     constraint18: 
     forall(c in ship){ 
       sum(j in toports:j!=1) G[c][1][j]<=1; 
       sum(j in toports)G[c][1][j]==0 => sum(i in fromports, j in toports)G[c][i][j]==0; 
     }        
     constraint19: 
     forall(c in ship){ 
       sum(i in fromports:i!=1) G[c][i][1]<=1; 
       sum(i in fromports)G[c][i][1]==0 => sum(i in fromports, j in toports)G[c][i][j]==0; 
     }   
     constraint20: 
     forall (c in ship,j in toports){ 
       sum(i in fromports:i!=j)G[c][i][j]-sum(i in toports:i!=j)G[c][j][i]==0; 
     }    
     constraint21: 
     forall(i in fromports: i != 1, j in toports, c in ship:j != 1) { 
      if (i != j) { 
         u[j] >= u[i] + 1 - 99999999*(1-G[c][i][j]); 
      } 
   }  	
} 
execute RESULT {
    var file = new IloOplOutputFile("Result.txt");
    file.writeln("Objective:", cplex.getObjValue());
     for (var Arc in PArc) { 
     var i = Arc.Origin;
     var j = Arc.Destination;
		 for (var e in OD) {
            for (var s in rangeS) {
               if (X[e][s][Arc] == 1 && i == e.Origin && j != e.Destination) {
                //file.writeln("Ship ", s, " of ", e, " deliver from ", i, " to ", j); 
                file.write(Arc.Destination," ");      
                }}}}  
     file.writeln();  
     for (var Arc in PArc) { 
     var i = Arc.Origin;
     var j = Arc.Destination;
		 for (var e in OD) {
            for (var s in rangeS) {
               if (X[e][s][Arc] == 1 && i == e.Origin && j != e.Destination) {
                //file.writeln("Ship ", s, " of ", e, " deliver from ", i, " to ", j); 
                file.write(s," ");            
                }}}}  
     file.writeln();   
     for (var o in OrgSet) {
       	file.write(o, " ")          
          }           	
    file.close();
}
