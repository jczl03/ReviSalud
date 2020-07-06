from flask import Flask, request, render_template,redirect,url_for 
import datetime  #Esta libreria funciona para manejar el tema de fechas
from datetime import date, time,datetime,timedelta
app = Flask(__name__) #Aqui se crea la variable sobre la que estarán el resto de rutas 
datos_personales={} #Aquí se almacenarán las cc como llaves y una lista de los datos personales como valores
historia_clinica={} #Aquí irá como llaves las cc y como valores una listas o diccionarios o diccionarios anidados, no recuerdo gg con los datos personales,obvio
contraseñas={"admin":"12341234"} #Aqui estarían almacenadas las contraseñas de los usuarios, también la del admin
personal_medico={} #Aquí irían los datos de cada médico, que el admin agregaría, pero de momento, lo tengo así para no complicarme registrando un médico cada vez que quiero probar algo
contra_medicos={} #Aquí iria la contraseña de los médicos funcionando de forma literalmente identica a la de los users
citas_pacientes={}
citas_medicos={}
lugares={}
especialidades={}
hora_inicio_jornada="00:00"
hora_final_jornada="23:59"
def sumatime(hora1,tiempo):
    hora1=hora1.split(":")
    h1=int(hora1[0])
    m1=int(hora1[1])
    m=m1+int(tiempo)
    mn=m%60
    hn=h1+(m//60)
    if mn<10:
        mn="0"+str(mn)
    if hn<10:
        hn="0"+str(hn)
    return str(hn)+":"+str(mn)
def filtro(medico,fecha,fechaf,especialidad,dicc):
    if medico!="" and dicc["medico"]!=medico:
        return False
    if especialidad!="" and dicc["especialidad"]!=especialidad:
        return False
    if fecha!="" and dicc["fecha"]<fecha:
        return False
    if fechaf!="" and dicc["fecha"]>fechaf:
        return False
    return True
def sumadia(fecha,fact):
    fecha = datetime.strptime(fecha, "%Y-%m-%d")
    fecha+= timedelta(days=fact)
    return str(fecha).split()[0]
def edad_usuario(datos_personales,cc): #Ya que la edad del usuario no será una variable fija, esta función determina la edad a partir de la fecha de nacimiento en formato aaaa-mm-dd
    fecha_de_nacimiento=str(datos_personales[cc][4])  
    x=fecha_de_nacimiento.split("-")
    a=str(date.today()).split("-")
    ano_a=int(a[0])
    mes_a=int(a[1]) 
    dia_a=int(a[2])
    dia=int(x[2])
    mes=int(x[1])
    ano=int(x[0])
    a=ano_a-ano
    m=mes_a-mes
    d=dia_a-dia
    if m>=0:
        if m==0:
            if d>=0:
                return a
            else:
                return int(a-1)
        else:
            return int(a)
    else:
        return int(a-1)
def estado_horario(fecha,horai):
    hora=str(datetime.now().hour)+":"+str(datetime.now().minute)
    if str(date.today())>=fecha:
        if str(date.today())==fecha:
            if horai<=hora:
                return False
        else:
            return False
    return True
def horario_valido(medic,fecha,hora_i,hora_f,lugar):
    hora=str(datetime.now().hour)+":"+str(datetime.now().minute)
    if hora_i<hora_inicio_jornada or hora_i>hora_final_jornada or hora_f<hora_inicio_jornada or hora_f>hora_final_jornada:
        return False
    if fecha<= str(date.today()):
        if fecha==str(date.today()):
            if hora_i<=hora:
                return False    
        else:
            return False
    if hora_i>=hora_f:
        return False
    for x in citas_medicos[medic]:
        if x["fecha"]==fecha:
            if (x["hora_inicial"]<hora_f and x["hora_final"]>=hora_f) or (x["hora_inicial"]<=hora_i and x["hora_final"]>hora_i):
                return False
    if fecha in lugares[lugar]:
        for horas in range(len(lugares[lugar][fecha])):
            if (hora_i<lugares[lugar][fecha][horas]["fin"] and lugares[lugar][fecha][horas]["inicio"]<=hora_i) or (hora_f<=lugares[lugar][fecha][horas]["fin"] and lugares[lugar][fecha][horas]["inicio"]<hora_f):
                return False
    return True
def agendamientovalido(cc,datoscita):
    horainicial=datoscita["hora_inicial"]
    horafinal=datoscita["hora_final"]
    fecha=datoscita["fecha"]
    especialidad=datoscita["especialidad"]
    c=0
    for cita in citas_pacientes[cc]:
        if cita["estado"]==True:
            if estado_horario(fecha,horainicial):
                c+=1
                if c==3:
                    return False
                if fecha==cita["fecha"] and ((cita["hora_inicial"]<=horainicial and horainicial<cita["hora_final"]) or (cita["hora_inicial"]<horafinal and horafinal<=cita["hora_final"])):
                    return False
                if cita["especialidad"]==especialidad:
                    return False
            else:
                cita["estado"]=False
            
    return True
@app.route('/') # En la ruta "/" estará la pagina inicial 
def home():
    return render_template('home.html') #Aqui se importa el html de home
@app.route('/registro')
def registro():
    return render_template('registro1.html')  #Aqui el usuario verifica sus datos para configurar su contraseña
@app.route('/log_in') #Aqui el user se debe loggear
def log_in():
    return render_template('login.html')
@app.route('/log_inmedic')
def log_inmedic():  #Login pero del personal medico
    return render_template('loginmedic.html')
@app.route('/logginmedic') #Luego del loggeo de los medicos, puede suceder 3 casos *más el caso de que sea el admin
def loggin2():
    medico=request.args['username']
    contraseña=request.args['password']
    if medico=="admin" and contraseña==contraseñas["admin"]:
        return redirect(url_for("home_admin")) #si es el admin, retornará el home de admin
    else:
        if medico in personal_medico:
            if contraseña==contra_medicos[medico]:
                return redirect(url_for('home_medic',medic=medico)) #Contraseña correcta, todo ok, redirige a homemedic
            else:
                return render_template('contraseñaincorrecta.html') #Contraseña incorrecta **Hacer una para medicos
        else:
            return render_template('usuarionoregistradologin.html').format(medico)  #Personal no registrado, no está en el diccionario contra_medicos **hacer pa medicos
@app.route('/home_user<cc>')
def home_user(cc):
    a=datos_personales[cc][0]+" "+datos_personales[cc][1]
    return render_template('homeuser.html', cc=cc).format(a) #Retorna el home en la que están los datos personales y las notas médicas
@app.route('/citasdisponibles<cc>')
def vercitas(cc):
    citas=["""<container ><table border WIDTH="990" ><tr><th>Especialidad</th><th>Fecha</th> <th>Hora</th><th>Médico</th><th>Lugar</th><td></td> </tr>"""]
    diccionario={}
    for x in personal_medico:
        if citas_medicos[x]!=[]:
            for i in range(len(citas_medicos[x])):
                if citas_medicos[x][i]["estado"]:
                    if not estado_horario(citas_medicos[x][i]["fecha"],citas_medicos[x][i]["hora_inicial"]):
                        citas_medicos[x][i]["estado"]=False
                if citas_medicos[x][i]["paciente"]==None and citas_medicos[x][i]["estado"]:
                    time=citas_medicos[x][i]["hora_inicial"]+"-"+citas_medicos[x][i]["hora_final"]
                    f=x+"-"+str(i)
                    llave=citas_medicos[x][i]["fecha"]+time+citas_medicos[x][i]["especialidad"]
                    diccionario[llave]=render_template('tablacitas.html', cc=cc).format(citas_medicos[x][i]["especialidad"],citas_medicos[x][i]["fecha"],time,citas_medicos[x][i]["medico"],citas_medicos[x][i]["lugar"],f)
    citas_ordenadas=sorted(list(diccionario))
    for t in citas_ordenadas:
        citas.append(diccionario[t])
    if citas==["""<container ><table border WIDTH="990" ><tr><th>Especialidad</th><th>Fecha</th> <th>Hora</th><th>Médico</th><th>Lugar</th><td></td> </tr>"""]:
        t="<h1>No hay citas disponibles</h1>"
    else:
        citas.append("</table></container>")
        t="".join(citas)
    return render_template('citasdisponibles.html',cc=cc).format(t)
@app.route('/usuarios')
def usuarios():
    return render_template('usuarios.html')
@app.route('/verusuarios')
def verusuarios():
    tabla=[]
    for x in datos_personales:
        n=datos_personales[x]
        sexo=n[3][0]
        tabla.append(render_template('tablausuarios.html').format(n[2],n[1],n[0],sexo,n[4],n[5],n[6],n[7]))
    if tabla==[]:
        tabla="<h3>Aún no hay usuarios registrados</h3>"
    else:
        tabla.sort()
        tabla='<container ><table border WIDTH="990" ><tr><th>Cédula</th><th>Apellidos</th><th>Nombres</th><th>Sexo</th><th>Fecha de Nacimiento</th><th>Telefono</th><th>Ciudad:</th><th>Dirección</th></tr>'+"".join(tabla)+"</table></container>"
    return render_template('verusuarios.html').format(tabla)
@app.route('/personalmedico')
def personalmedico():
    return render_template('personalmedico.html')
@app.route('/verpersonal_medico')
def vermedicos():
    tabla=[]
    for x in personal_medico:
        n=personal_medico[x]
        sexo=n[3][0]
        tabla.append(render_template('tablamedicos.html').format(n[2],n[4],n[1],n[0],sexo))
    if tabla==[]:
        tabla="<h3>Aún no hay personal médico registrado</h3>"
    else:
        tabla='<container ><table border WIDTH="990" ><tr><th>Cédula</th><th>Especialidad</th><th>Apellidos</th><th>Nombres</th><th>Sexo</th></tr>'+"".join(tabla)+"</table></container>"
    return render_template('vermedicos.html').format(tabla)

@app.route('/citas-disponibles<cc>', methods=["POST","GET"]) #Filtro para las citas
def citas_filtradas(cc):
    if request.method=="POST":
        medico=request.form['medic']
        fecha=request.form['fecha']
        fechaf=request.form['fechaf']
        especialidad=request.form['especialidad']
        citas=["""<container ><table border WIDTH="990" ><tr><th>Especialidad</th><th>Fecha</th> <th>Hora</th><th>Médico</th><th>Lugar</th><td></td> </tr>"""]
        diccionario={}
        for x in personal_medico:
            if citas_medicos[x]!=[]:
                for i in range(len(citas_medicos[x])):
                    if citas_medicos[x][i]["estado"]:
                        if not estado_horario(citas_medicos[x][i]["fecha"],citas_medicos[x][i]["hora_inicial"]):
                            citas_medicos[x][i]["estado"]=False
                    if citas_medicos[x][i]["paciente"]==None and citas_medicos[x][i]["estado"] and filtro(medico,fecha,fechaf,especialidad,citas_medicos[x][i]):
                        time=citas_medicos[x][i]["hora_inicial"]+"-"+citas_medicos[x][i]["hora_final"]
                        f=x+"-"+str(i)
                        llave=citas_medicos[x][i]["fecha"]+time+citas_medicos[x][i]["especialidad"]
                        diccionario[llave]=render_template('tablacitas.html', cc=cc).format(citas_medicos[x][i]["especialidad"],citas_medicos[x][i]["fecha"],time,citas_medicos[x][i]["medico"],citas_medicos[x][i]["lugar"],f)
        citas_ordenadas=sorted(list(diccionario))
        for t in citas_ordenadas:
            citas.append(diccionario[t])
        if citas==["""<container ><table border WIDTH="990" ><tr><th>Especialidad</th><th>Fecha</th> <th>Hora</th><th>Médico</th><th>Lugar</th><td></td> </tr>"""]:
            t="<h1>No hay citas disponibles</h1>"
        else:
            citas.append("</table></container>")
            t="".join(citas)
        return render_template('citasdisponibles.html',cc=cc).format(t)
    else:
        medicos=[]
        for n in personal_medico:
            nombremedico=personal_medico[n][0]+" "+personal_medico[n][1]
            medicos.append(nombremedico)
        doc=['<select name="medic" size="1">','<option value="">---</option>']
        for x in sorted(medicos):
            doc.append(render_template('listar.html').format(x))
        doc="".join(doc)+"</select>"
        esp=['<select name="especialidad" size="1">','<option value="">---</option>']
        for x in sorted(list(especialidades.keys())):
            esp.append(render_template('listar.html').format(x))
        esp="".join(esp)+"</select>"
        return render_template('filtrarcitas.html',cc=cc).format(doc,esp) #doctores y especialidades
@app.route('/citasmedicasm<medic>')
def citas_medicas_medic(medic):
    return render_template('citasmedicasmedic.html',medic=medic)
@app.route('/vercitasmedic<medic>')
def ver_citas_medic(medic):
    if citas_medicos[medic]==[]:
        citas="<h1>No tiene citas</h1>"
    else:
        citas=["""<container ><table border WIDTH="990" ><tr><th>Especialidad</th><th>Fecha</th> <th>Hora</th><th>Paciente (CC)</th><th>Lugar</th></tr>"""]
        diccionario={}
        for i in range(len(citas_medicos[medic])):
            if citas_medicos[medic][i]["estado"]:
                if not estado_horario(citas_medicos[medic][i]["fecha"],citas_medicos[medic][i]["hora_inicial"]):
                    citas_medicos[medic][i]["estado"]=False
            if citas_medicos[medic][i]["estado"]:
                time=citas_medicos[medic][i]["hora_inicial"]+"-"+citas_medicos[medic][i]["hora_final"]
                if citas_medicos[medic][i]["paciente"]==None:
                    paciente="<i>No está reservada</i>"
                else:
                    paciente=citas_medicos[medic][i]["paciente"]
                llave=citas_medicos[medic][i]["fecha"]+time
                diccionario[llave]=render_template('tablacitasmedic.html').format(citas_medicos[medic][i]["especialidad"],citas_medicos[medic][i]["fecha"],time,paciente,citas_medicos[medic][i]["lugar"])
        citas_ordenadas=sorted(list(diccionario))
        for n in citas_ordenadas:
            citas.append(diccionario[n])
        citas.append("</table></container>")
        if citas==["""<container ><table border WIDTH="990" ><tr><th>Especialidad</th><th>Fecha</th> <th>Hora</th><th>Paciente (CC)</th><th>Lugar</th></tr>""","</table></container>"]:
            citas="<h1>No tiene citas</h1>"
        else:
            citas="".join(citas)
    return render_template('vercitasmedic.html',medic=medic).format(citas)
@app.route('/generarcitas<medic>')
def generar_citas(medic):
    lug=['<select name="lugar" size="1">']
    for x in sorted(list(lugares.keys())):
        lug.append(render_template('listar.html').format(x))
    lug="".join(lug)+"</select>"
    return render_template('generarcitas.html',medic=medic).format(lug)
@app.route('/citasgeneradas<medic>',methods=["POST"])
def citas_generadas(medic):
    horai= str(request.form['horai'])#Aqui tomaría la hora inicial
    fecha= str(request.form['fecha'])#fecha inicial
    fechafin=str(request.form['fechafin']) #Fecha fin xd
    limite= str(request.form['limite'])#hora final
    intervalo=int(request.form['intervalo'])#tiempo xd
    lugar= str(request.form['lugar'])#Lugar xd
    validas=[]
    invalidas=[]
    while fecha<=fechafin:
        hora_i=horai
        while hora_i<limite and hora_i<=hora_final_jornada and hora_i>=hora_inicio_jornada and sumatime(hora_i,intervalo)<=limite:
            horaf=sumatime(hora_i,intervalo) #Esta funcion esta en otro .py
            if horario_valido(medic,fecha,hora_i,horaf,lugar) and horaf<=limite:
                nomape=personal_medico[medic][0]+" "+personal_medico[medic][1]
                datoscita={"fecha":fecha,"hora_final":horaf,"hora_inicial":hora_i,"lugar":lugar,"medico":nomape,"especialidad":personal_medico[medic][4],"paciente":None,"estado":True}
                validas.append(render_template('validosinvalidos.html').format(fecha,hora_i,horaf)) 
                citas_medicos[medic].append(datoscita)
            else:
                invalidas.append(render_template('validosinvalidos.html').format(fecha,hora_i,horaf))
            hora_i=horaf
        fecha=sumadia(fecha,1)
    if len(invalidas)>0:
        if len(validas)>0:
            p1=['<table border WIDTH="990">',render_template('validosinvalidos.html').format("<b>Fecha</b>","<b>Hora Inicio</b>","<b>Hora Final</b>")] #Hay que crear una "base" y una "tapa"
            for x in invalidas:
                p1.append(x) #Crear base, tabla que diga error, sla cita no ha sido creada pues su horario no es válido
            p2=['<table border WIDTH="990">',render_template('validosinvalidos.html').format("<b>Fecha</b>","<b>Hora Inicio</b>","<b>Hora Final</b>")] #Hay que crear una "base" y una "tapa"
            for x in validas:
                p2.append(x)
            p1="".join(p1)+"</table>"
            p2="".join(p2)+"</table>"
            return render_template('citasgeneradasinvalidas.html',medic=medic).format(p2,p1) #Template con dos jumbotrones xd
        else:
            return render_template('citasinvalidas.html',medic=medic)
    else:
        return render_template('citasgeneradas.html',medic=medic) #Un jumbotron que diga todas las citas fueron generadas con éxito

    

@app.route('/agendarcita<cc>')
def agendarcita(cc):
    f=request.args['f']
    f=f.split("-")
    x=f[0]
    i=int(f[1])
    if citas_medicos[x][i]["paciente"]==None and citas_medicos[x][i]["estado"]==True and agendamientovalido(cc,citas_medicos[x][i],): #aqui voy xd
        citas_medicos[x][i]["paciente"]=cc
        codigo="-".join(f)
        citas_medicos[x][i]["codigo"]=codigo
        citas_pacientes[cc].append(citas_medicos[x][i])
        return render_template('citaagendada.html', cc=cc).format(citas_medicos[x][i]["medico"],citas_medicos[x][i]["especialidad"],citas_medicos[x][i]["fecha"],citas_medicos[x][i]["hora_inicial"],citas_medicos[x][i]["hora_final"],citas_medicos[x][i]["lugar"])
    else:
        return render_template('erroragendamiento.html',cc=cc) #Debo crear un templATE 
@app.route('/miscitas<cc>')
def mis_citas(cc):
    mc=["""<container ><table border WIDTH="990" ><tr><th>Especialidad</th><th>Fecha</th> <th>Hora</th><th>Médico</th><th>Lugar</th><td></td> </tr>"""]
    if citas_pacientes[cc]!=[]:
        for i in range(len(citas_pacientes[cc])):
            if citas_pacientes[cc][i]["estado"]:
                if not estado_horario(citas_pacientes[cc][i]["fecha"],citas_pacientes[cc][i]["hora_inicial"]):
                    citas_pacientes[cc][i]["estado"]=False
            if citas_pacientes[cc][i]["estado"]: 
                time=citas_pacientes[cc][i]["hora_inicial"]+"-"+citas_pacientes[cc][i]["hora_final"]
                mc.append(render_template('tablacitas2.html', cc=cc).format(citas_pacientes[cc][i]["especialidad"],citas_pacientes[cc][i]["fecha"],time,citas_pacientes[cc][i]["medico"],citas_pacientes[cc][i]["codigo"],i,citas_pacientes[cc][i]["lugar"]))
        mc.append("</table></container>")
        mc="".join(mc)
    else:
        mc="<h1>No tienes citas programadas</h1>"
    if mc==["""<container ><table border WIDTH="990" ><tr><th>Especialidad</th><th>Fecha</th> <th>Hora</th><th>Médico</th><th>Lugar</th><td></td> </tr>""","</table></container>"]:
        mc="<h1>No tienes citas programadas</h1>"
    return render_template('miscitas.html', cc=cc).format(mc)
@app.route('/cancelarcita<cc>')
def cancelar_cita(cc):
    f=request.args['f']
    f=f.split("-")
    x=f[0]
    i=int(f[1])
    u=request.args['u']
    citas_medicos[x][i]["paciente"]=None
    citas_pacientes[cc].pop(int(u))
    return render_template('citacancelada.html', cc=cc)
@app.route('/historiamedica<cc>')
def ver_historia_medica(cc):
    a=datos_personales[cc][0]+" "+datos_personales[cc][1]  #a es nombres+apellidos, para el saludo inicial :v
    notas_medicas=[] #Aqui se agregaran las notas medicas (consultas, ya convertidas a tabla, para luego unirlas)
    nm=["""<container ><table border WIDTH="990" ><tr><th colspan="3">Notas Médicas</th>"""] #Esta sería como la cabeza de la tabla  
    if historia_clinica[cc]["consultas"]==[]: #Si no se han hecho notas medicas...
        nm.append("""<tr><td colspan="3"><i>No especifica notas médicas</i></td></tr>""") 
    else:
        for x in historia_clinica[cc]["consultas"]: #Cada consulta...
            nm.append(render_template('tabla.html').format(x["fecha"],x["nombre"],x["especialidad"],x["motivo"],x["revision"],x["examen"],x["diagnostico"],x["tratamiento"]))    #Usa la plantilla html de las tablas, remplazando los valores por los de la nota **
    nm.append("</table></container>") #Cierre de la tabla
    nm="".join(nm) #Une las sub tablas, por llamarlas de alguna forma
    antecedentes=["""<container ><table border WIDTH="990" ><tr><th colspan="2">Antecedentes</th></tr><tr><th>Tipo de Antecedente</th><th>Detalle</th></tr>"""]
    if historia_clinica[cc]["antecedentes"]==[]:
        antecedentes.append('<td colspan="2"><i>No especifica antecedentes</i></td>')
    else:
        for j in historia_clinica[cc]["antecedentes"]:
            antecedentes.append('<tr><td>{0}</td><td>{1}</td></tr>'.format(j["patologico"],j["detalle"]))
    antecedentes.append("</table></container>")
    antecedentes="".join(antecedentes)
    peso=historia_clinica[cc]["peso"]
    if peso==None:
        peso="<i>No especifica</i>"
    talla=historia_clinica[cc]["altura"]
    if talla==None:
        talla="<i>No especifica</i>"
    return render_template('verhistoriamedica.html', cc=cc).format(a,cc,datos_personales[cc][3],datos_personales[cc][4],edad_usuario(datos_personales,cc),datos_personales[cc][5],datos_personales[cc][6],datos_personales[cc][7],peso,talla,nm,antecedentes)
@app.route('/solicitarhistoria<medic>')
def solicitar_historia(medic):
    return render_template('pedirhistoria.html', medic=medic)
@app.route('/verhistoriaclinica<medic>')
def ver_historia_clinica(medic):
    cc=request.args['username']
    if cc in datos_personales:
        a=datos_personales[cc][0]+" "+datos_personales[cc][1]  #a es nombres+apellidos, para el saludo inicial :v
        notas_medicas=[] #Aqui se agregaran las notas medicas (consultas, ya convertidas a tabla, para luego unirlas)
        nm=["""<container ><table border WIDTH="990" ><tr><th colspan="3">Notas Médicas</th>"""] #Esta sería como la cabeza de la tabla  
        if historia_clinica[cc]["consultas"]==[]: #Si no se han hecho notas medicas...
            nm.append("""<tr><td colspan="3"><i>No especifica notas médicas</i></td></tr>""") 
        else:
            for x in historia_clinica[cc]["consultas"]: #Cada consulta...
                nm.append(render_template('tabla.html').format(x["fecha"],x["nombre"],x["especialidad"],x["motivo"],x["revision"],x["examen"],x["diagnostico"],x["tratamiento"]))    #Usa la plantilla html de las tablas, remplazando los valores por los de la nota **
        nm.append("</table></container>") #Cierre de la tabla
        nm="".join(nm) #Une las sub tablas, por llamarlas de alguna forma
        antecedentes=["""<container ><table border WIDTH="990" ><tr><th colspan="2">Antecedentes</th></tr><tr><th>Tipo De Antecedente</th><th>Detalle</th></tr>"""]
        if historia_clinica[cc]["antecedentes"]==[]:
            antecedentes.append('<td colspan="2"><i>No especifica antecedentes</i></td>')
        else:
            for j in historia_clinica[cc]["antecedentes"]:
                antecedentes.append('<tr><td>{0}</td><td>{1}</td></tr>'.format(j["patologico"],j["detalle"]))
        antecedentes.append("</table></container>")
        antecedentes="".join(antecedentes)
        peso=historia_clinica[cc]["peso"]
        if peso==None:
            peso="<i>No especifica</i>"
        talla=historia_clinica[cc]["altura"]
        if talla==None:
            talla="<i>No especifica</i>"
        return render_template('verhistoriamedica-medic.html', medic=medic).format(a,cc,datos_personales[cc][3],datos_personales[cc][4],edad_usuario(datos_personales,cc),datos_personales[cc][5],datos_personales[cc][6],datos_personales[cc][7],peso,talla,nm,antecedentes)
    else:
        return render_template('pacientenoregistrado.html',medic=medic).format(cc)
@app.route('/loggin') #Aqui se viene despues de el loggin de usuario, con las 3 posibilidades
def loggin():
    cc=request.args['username']
    contraseña=request.args['password']
    if cc=="admin" and contraseña==contraseña==contraseñas["admin"]:
        return redirect(url_for("home_admin"))
    else:
        
        if cc in datos_personales:
            if contraseña==contraseñas[cc]:
                return redirect(url_for('home_user',cc=cc)) #todo ok
            else:
                return render_template('contraseñaincorrecta.html')  #...
        else:
                return render_template('usuarionoregistradologin.html').format(cc) #No está registrado
@app.route('/home_medic<medic>')
def home_medic(medic):
    nomape=personal_medico[medic][0]+" "+personal_medico[medic][1]
    return render_template('homemedic.html', medic=medic).format(nomape) #... *De momento no tiene casi nada
@app.route('/historiaclinica<medic>')
def historia_clinica_(medic):
    return render_template('historiaclinica.html',medic=medic)
@app.route('/añadircita<medic>')
def añadir_citas(medic):
    lug=['<select name="lugar" size="1">']
    for x in sorted(list(lugares.keys())):
        lug.append(render_template('listar.html').format(x))
    lug="".join(lug)+"</select>"
    return render_template('añadircita.html',medic=medic).format(lug)
@app.route('/añadircitanice<medic>',methods=["POST"])
def añadir_citas2(medic):
    fecha=str(request.form['fecha'])
    horai=str(request.form['hora'])
    horaf=str(request.form['hora2'])
    lugar=request.form['lugar'].strip().upper()
    if horario_valido(medic,fecha,horai,horaf,lugar):
        if fecha not in lugares:
            lugares[lugar][fecha]=[{"inicio":horai,"fin":horaf}]
        else:
            lugares[lugar][fecha].append({"inicio":horai,"fin":horaf})
        nomape=personal_medico[medic][0]+" "+personal_medico[medic][1]
        datoscita={"fecha":fecha,"hora_final":horaf,"hora_inicial":horai,"lugar":lugar,"medico":nomape,"especialidad":personal_medico[medic][4],"paciente":None,"estado":True}
        citas_medicos[medic].append(datoscita)
        return render_template('pruebacita.html',medic=medic).format(datoscita)
    else:
        return render_template('horarioinvalido.html', medic=medic)#render_template() #Crear template que diga horario no válido
@app.route('/modificarhistoriaclinica<medic>')
def modificar_citas_medicas(medic):
    return render_template('modificarhistoriaclinica.html', medic=medic)
@app.route('/editartallaypeso<medic>')
def editar_talla_peso(medic):
    return render_template('editartallaypeso.html', medic=medic)
@app.route('/cambiartallaypeso<medic>')
def cambiar_peso_talla(medic):
    cc=request.args['cedula']
    if cc in datos_personales:
        peso=request.args['peso']
        talla=request.args['talla']
        if peso!="":
            historia_clinica[cc]["peso"]=peso
        if talla!="":
            historia_clinica[cc]["altura"]=talla
        return render_template('tallaypesocambiados.html',medic=medic)
    else:
        return render_template('pacientenoregistrado.html',medic=medic).format(cc)
@app.route('/añadirantecedente<medic>')
def añadir_antecedente(medic):
    return render_template('añadirantecedente.html',medic=medic)
@app.route('/antecedenteañadido<medic>')
def antecedente_añadido(medic):
    cc=request.args['cedula']
    if cc in datos_personales:
        patologico=request.args['patologico']
        detalle=request.args['detalle']
        if patologico!="":
            dic={"patologico":patologico,"detalle":detalle}
            historia_clinica[cc]["antecedentes"].append(dic)
            return render_template('antecedenteañadido.html', medic=medic) 
        else:
            return render_template('parametrovaciomedic.html', medic=medic)
    else:
        return render_template('pacientenoregistrado.html',medic=medic).format(cc)


@app.route('/añadir_nota_medica<medic>') #funcion a la que se accede desde homemedic
def agregar_nota_medica(medic):
        return render_template('añadirnotamedica.html', medic=medic) #html en el que se solicitan los campos para la nota médica
@app.route('/notamedica<medic>',methods=["POST"])
def notamedica(medic):
    cc=request.form['cedula'] #La cc del paciente a la que se quiere agregar la nota médica
    if cc in datos_personales: #Verifica que el usuario exista
        fecha=str(date.today())
        especialidad="especialidad" #escpecialidad xdxd
        motivo=request.form['motivo']
        revisionxsistemas=request.form['revision']
        examen=request.form['examen']
        diagnostico=request.form['diagnostico']
        tratamiento=request.form['tratamiento']
        #ccmedico=request.form['medico']
        ccmedico=medic
        especialidad=personal_medico[ccmedico][4]
        nombre=personal_medico[ccmedico][0]+" "+personal_medico[ccmedico][1]
        notamedica={"especialidad":especialidad,"nombre":nombre,"fecha":fecha,"motivo":motivo,"revision":revisionxsistemas,"examen":examen,"diagnostico":diagnostico,"tratamiento":tratamiento} #,"medico":medico}
        historia_clinica[cc]["consultas"].append(notamedica)
        return render_template('pruebanotamedica.html', medic=medic) #** Hay que pensar en que que poner, esto lo puse por probar solamente
    else:
            return render_template('usuarionoregistrado.html').format(cc) #Si el usuario no existe... gg **Reusé esta plantilla, hay que hacer una para que no retorne
@app.route('/admin')      
def home_admin():
    return render_template('admin.html') #Home Admin
@app.route('/admincambiarcontraseña')
def cambio_contra_admin():
    return render_template('cambiarcontraadmin.html') #crear html que pida la contraseña actual
@app.route('/admin-cambiarcontraseña-nuevacontraseña', methods=["POST","GET"])
def nueva_contraseña_admin():
    contra=request.form['contra']
    if contra==contraseñas["admin"]: 
        return render_template('cambiocontraadmin.html') #Pida contraseña y confirmar la contraseña
    else:
        return render_template('contraincorrectacambioadmin.html') #Que diga que la contraseña es incorrecta y tenga un boton que redirija a /cambiarcontraseñaadmin
@app.route('/admin-cambiarcontraseña-cambiocontraseña', methods=["POST","GET"])
def contraseña_cambiada_admin():
    contra_nueva0=request.form['nueva']
    contra_nueva1=request.form['nueva2']
    if contra_nueva0==contra_nueva1:
        contraseñas["admin"]=contra_nueva0
        return render_template('contraseñaadmincambiada.html') #Que diga contraseña cambiada 
    else:
        return render_template('cambiocontraadminincongruente.html') #Contraseñas incongruente, botoncito que regirija a /cambiarcontraseñaadmin
#### cambiar contraseña usuario
@app.route('/home_usercambiarcontraseña<cc>')
def cambio_contra_user(cc):
    return render_template('cambiarcontrauser.html', cc=cc) #crear html que pida la contraseña actual
@app.route('/home_usercambiarcontraseñanuevacontraseña<cc>', methods=["POST","GET"])
def nueva_contraseña_user(cc):
    contra=request.form['contra']
    if contra==contraseñas[cc]: 
        return render_template('cambiocontrauser.html', cc=cc) #Pida contraseña y confirmar la contraseña
    else:
        return render_template('contraincorrectacambiouser.html', cc=cc) #Que diga que la contraseña es incorrecta y tenga un boton que redirija a /cambiarcontraseñaadmin
@app.route('/home_usercambiarcontraseñacambiocontraseña<cc>', methods=["POST","GET"])
def contraseña_cambiada_user(cc):
    contra_nueva0=request.form['nueva']
    contra_nueva1=request.form['nueva2']
    if contra_nueva0==contra_nueva1:
        contraseñas[cc]=contra_nueva0
        return render_template('contraseñausercambiada.html', cc=cc) #Que diga contraseña cambiada 
    else:
        return render_template('cambiocontrauserincongruente.html', cc=cc)
# ####Cambio contraseña de medicos
@app.route('/home_mediccambiarcontraseña<medic>')
def cambio_contra_medic(medic):
    return render_template('cambiarcontramedic.html', medic=medic) #crear html que pida la contraseña actual
@app.route('/home_mediccambiarcontraseñanuevacontraseña<medic>', methods=["POST","GET"])
def nueva_contraseña_medic(medic):
    contra=request.form['contra']
    if contra==contra_medicos[medic]: 
        return render_template('cambiocontramedic.html', medic=medic) #Pida contraseña y confirmar la contraseña
    else:
        return render_template('contraincorrectacambiomedic.html', medic=medic) #Que diga que la contraseña es incorrecta y tenga un boton que redirija a /cambiarcontraseñaadmin
@app.route('/home_mediccambiarcontraseñacambiocontraseña<medic>', methods=["POST","GET"])
def contraseña_cambiada_medic(medic):
    contra_nueva0=request.form['nueva']
    contra_nueva1=request.form['nueva2']
    if contra_nueva0==contra_nueva1:
        contra_medicos[medic]=contra_nueva0
        return render_template('contraseñamediccambiada.html', medic=medic) #Que diga contraseña cambiada 
    else:
        return render_template('contramedicincongruente.html', medic=medic)
##
@app.route('/validar_datos-validacion') #Aqui se validan los datos del registro
def validar_datos2():
        nombre=request.args['nombres'].strip().upper()
        apellidos=request.args['apellidos'].strip().upper()
        cc=request.args['cedula'].strip()
        sexo=request.args['sexo'].strip().upper()
        fecha_nacimiento=str(request.args['fecha_nacimiento'])
        edad=int(request.args['edad'].strip())
        if cc in contraseñas and cc in datos_personales:
            if contraseñas[cc]==None:
                tupla=datos_personales[cc]
                if tupla[0]==nombre and tupla[1]==apellidos and tupla[3]==sexo and tupla[4]==fecha_nacimiento and edad==edad_usuario(datos_personales,cc): #Aquí se comparan los datos ingresados por el usuario con los del sistema (añadidos por el admin)
                    return redirect(url_for("crear_contraseña", cc=cc)) #Si coinciden, permite crear contraseña **
                else:
                    return render_template('datosincorrectos.html') #**
            else: 
                return render_template("usuarioyaregistrado.html").format(cc)
        else:
            return render_template('usuarionoregistrado.html').format(cc) #Si el usuario no ha sido registrado por el admin

    
@app.route('/crearcontraseña<cc>', methods=["POST","GET"])
def crear_contraseña(cc):
    if request.method=="POST":
        contraseña1=request.form['c1']
        contraseña2=request.form['c2']
        if contraseña1==contraseña2:
            contraseñas[cc]=contraseña1
            return render_template('contraseñacreada.html') 
        else:
            return render_template('contraseñasincongruentes.html')
    else:
        return render_template('crearcontraseña.html')
@app.route('/añadirlugar', methods=["POST","GET"])
def añadirlugar():
    if request.method=="POST":
        lugar=request.form['lugar'].strip().upper()
        lugares[lugar]={}
        return render_template('lugarañadido.html').format(lugar)
    else:
        return render_template('añadirlugar.html')
@app.route('/añadirespecialidad', methods=["POST","GET"])
def añadir_especialidad():
    if request.method=="POST":
        especialidad=request.form['especialidad'].strip().upper()
        especialidades[especialidad]=True
        return render_template('especialidadañadida.html').format(especialidad) #crear template que diga la especialidad x ha sido añadida
    else:
        return render_template('añadirespecialidad.html')#Crear template llamado añadir especialidad.html
@app.route('/crear_usuario')
def crear_usuario():
    return render_template('crearusuario.html')
@app.route('/crear_medico')
def crear_medico():
    esp=['<select name="especialidad" size="1">']
    for x in sorted(list(especialidades.keys())):
        esp.append(render_template('listar.html').format(x))
    esp="".join(esp)+"</select>"
    return render_template('crearmedico.html').format(esp)
def ver_datosm():
        nombre=request.args['nombres'].strip().upper()
        apellidos=request.args['apellidos'].strip().upper()
        cc=str(request.args['cc'].strip())
        try:
            int(cc)
        except:
            return render_template('usuariomalcreado.html')
        sexo=request.args['sexo'].strip().upper()
        especialidad=request.args['especialidad'].strip().upper()
        if cc not in personal_medico:
            personal_medico[cc]=(nombre,apellidos,cc,sexo,especialidad)
            contra=nombre[:2]+apellidos[:2]+cc[-4:] #La contraseña del médico corresponde a los 2 primeros digitos de su nombre+ 2 primeros de su apellido+ 4 ultimos de la cc, para la entrega final hay que crear la función de cambio de clave y esas cosas
            contra_medicos[cc]=contra
            citas_medicos[cc]=[]
            return render_template('medicobiencreado.html') 
        else:
            return render_template('usuariorepetido.html').format(cc)
@app.route('/verificar_datosm')
def verificar_datosm():
    return ver_datosm()

def ver_datos():
        nombre=request.args['nombres'].strip().upper()
        apellidos=request.args['apellidos'].strip().upper()
        sexo=request.args['sexo'].strip().upper()
        fecha_nacimiento=str(request.args['fecha_nacimiento'])
        cc=str(request.args['cc'].strip())
        telefono=str(request.args['telefono'].strip())
        try:
            int(cc)
            int(telefono)
        except:
            return render_template('usuariomalcreado.html')

        ciudad_residencia=request.args['ciudad'].strip().upper()
        residencia=request.args['direccion'].strip().upper()
        if cc not in datos_personales :
            datos_personales[cc]=(nombre,apellidos,cc,sexo,fecha_nacimiento,telefono,ciudad_residencia,residencia)
            contraseñas[cc]=None
            historia_clinica[cc]={"peso":None,"altura":None,"antecedentes":[],"consultas":[]}
            citas_pacientes[cc]=[]
            return render_template('usuariocreadobien.html')
        else:
            return render_template('usuariorepetido.html').format(cc)         
@app.route('/verificar_datos')
def verificar_datos():
    return ver_datos()
@app.errorhandler(500)
def error(err):
    return render_template('internalservererror.html'),500
@app.errorhandler(404)
def error(err):
    return render_template('pagenotfound.html'),404

if __name__ == "__main__":
    app.run(debug=True)
 # Launch the FlaskPy dev server
 
