import os
import Program 

def agglomeration():
    dir=os.listdir()

    zipfiles=[x for x in dir if '.zip' in x ]
    extractedfolder=[x.replace('.zip',"") for x in zipfiles ]
    po=0
    for i in zipfiles:
        if extractedfolder[po] in dir:
            po=po+1
            continue
        else:        
            with ZipFile(i, 'r') as zip:
                zip.printdir()  
                # extracting all the files
                print('Extracting all the files now...')
                zip.extractall()
                print('Done!')
            po=po+1
    gpsfiles=[]
    for j in extractedfolder:
        files=os.listdir(j)
        txtfile=[x for x in files if '_gps_file.txt' in x]
        file=[[j],txtfile]
        gpsfiles.append(file)

    kml_filename	= "GPS_HazardsRedYellowGreen.kml"
    counterrrrr=0 
    stops=dict()


    gRed=dict()
    gYellow=dict()
    gGreen=dict()
    for k in gpsfiles:   
        gpsinfo1=[]    
        # print(k[0][0])
        for l in k[1]:        
            path=k[0][0]+"/"+l       
        
            gps_filename	= path
            
            
            
            
            
        
            gps_info	= {}  
            gps_info1	= {}  
            get_gps_data()
            gps_info1=gps_info.copy()
            

            
            remove_redundant_GPS_points()    
        
            
            stop=findStops()
            
        
            
            stops[l]=stop
            
    noofstops=list(stops.values())


    stopscoordinates=[]
    for i in noofstops:
        for j in range(3):
            if j==1:
                if i[j]==[]:
                    pass
                else:
                    for k in i[j]:
                        stopscoordinates.append(k)
            elif j==2:
                if i[j]==[]:
                    pass
                else:
                    for k in i[j]:
                        stopscoordinates.append(k)
            else:
                if i[j]==[]:
                    pass
                else:
                    for k in i[j]:
                        stopscoordinates.append(k)

            

    kml_file	= open(kml_filename, 'w+')
    kml_file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
    kml_file.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n")
    kml_file.write("<Document>\n")                    
    write_out_KML_file(gRed,'Red','ff0000ff')
    write_out_KML_file(gYellow,'Yellow','ff00ffff')
    write_out_KML_file(gGreen,'Green','ffffff00')

    kml_file.write("  </Document>\n")
    kml_file.write("</kml>\n")
    x=[]
    y=[]
    for m in stopscoordinates:
        x.append(m[0])
        y.append(m[1])
        
    plt.scatter(x,y)
    plt.title("Points On Map")
    plt.savefig("Scatterplot.jpg")
    plt.show()

        



    dummy = pd.DataFrame()
    dummy['x']=x
    dummy['y']=y


    den = dendrogram(linkage(dummy, method='centroid'), 
    labels = dummy.index)
    plt.ylabel('Distance between Clsuters', fontsize = 14)
    plt.title('Dendrogram of the Stops')
    plt.savefig('Dendogram.jpg')
    plt.show()

    # colors = np.array(["Red","Green","Blue","Orange","Purple","Yellow","Cyan","Teal","Brown","Black","Violet","Pink"])
    aglo = AgglomerativeClustering(n_clusters=12, affinity='euclidean', linkage='average')

    dummy['Aglo-label'] = aglo.fit_predict(dummy)





    Centroidx=[]
    Centroidy=[]
    for i in range(12):
        df1=dummy[dummy['Aglo-label'] ==i]
        
        npdfx=df1['x'].to_numpy()
        npdfy=df1['y'].to_numpy()
        xavg=np.average(npdfx)
        yavg=np.average(npdfy)
        Centroidx.append(xavg)
        Centroidy.append(yavg)

        
    plt.scatter(Centroidx,Centroidy)
    plt.title("Using Agglomerative Clustering")
    plt.savefig("CommonStops.jpg")

    plt.show()