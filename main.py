from pyobigram.utils import sizeof_fmt,get_file_size,createID,nice_time
from pyobigram.client import ObigramClient,inlineQueryResultArticle
from MoodleClient import MoodleClient
from JDatabase import JsonDatabase
import zipfile
import os
import infos
import shortener
import xdlink
import mediafire
import datetime
import time
import youtube
import NexCloudClient
from pydownloader.downloader import Downloader
from ProxyCloud import ProxyCloud
import ProxyCloud
import socket
import S5Crypto
import random
####################################################
saveconfig = "βConfiguraciΓ³n Guardada"
proxy_list = []
###################################################


#ef nameRamdom():
   # populaton = 'abcdefgh1jklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ'
   # name = "".join(random.sample(populaton,10))
   # return name
def downloadFile(downloader,filename,currentBits,totalBits,speed,time,args):
    try:
        bot = args[0]
        message = args[1]
        thread = args[2]
        if thread.getStore('stop'):
            downloader.stop()
        downloadingInfo = infos.createDownloading(filename,totalBits,currentBits,speed,time,tid=thread.id)
        bot.editMessageText(message,downloadingInfo)
    except Exception as ex: print(str(ex))
    pass

def uploadFile(filename,currentBits,totalBits,speed,time,args):
    try:
        bot = args[0]
        message = args[1]
        originalfile = args[2]
        thread = args[3]
        downloadingInfo = infos.createUploading(filename,totalBits,currentBits,speed,time,originalfile)
        bot.editMessageText(message,downloadingInfo)
    except Exception as ex: print(str(ex))
    pass

def processUploadFiles(filename,filesize,files,update,bot,message,thread=None,jdb=None):
    try:
        filename = filename.replace(" ", "_")
        bot.editMessageText(message,'π¦πΏπππππππππ ππππ πππππβ...')
        evidence = None
        fileid = None
        user_info = jdb.get_user(update.message.sender.username)
        cloudtype = user_info['cloudtype']
        proxy = ProxyCloud.parse(user_info['proxy'])
        if cloudtype == 'moodle':
            client = MoodleClient(user_info['moodle_user'],
                                  user_info['moodle_password'],
                                  user_info['moodle_host'],
                                  user_info['moodle_repo_id'],
                                  proxy=proxy)
            loged = client.login()
            itererr = 0
            if loged:
                if user_info['uploadtype'] == 'evidence':
                    evidences = client.getEvidences()
                    evidname = str(filename).split('.')[0]
                    for evid in evidences:
                        if evid['name'] == evidname:
                            evidence = evid
                            break
                    if evidence is None:
                        evidence = client.createEvidence(evidname)

                originalfile = ''
                if len(files)>1:
                    originalfile = filename
                draftlist = []
                for f in files:
                    f_size = get_file_size(f)
                    resp = None
                    iter = 0
                    tokenize = False
                    if user_info['tokenize']!=0:
                       tokenize = True
                    while resp is None:
                          if user_info['uploadtype'] == 'evidence':
                             fileid,resp = client.upload_file(f,evidence,fileid,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                             draftlist.append(resp)
                          if user_info['uploadtype'] == 'draft':
                             fileid,resp = client.upload_file_draft(f,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                             draftlist.append(resp)
                          if user_info['uploadtype'] == 'blog':
                             fileid,resp = client.upload_file_blog(f,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                             draftlist.append(resp)
                          if user_info['uploadtype'] == 'calendar':
                             fileid,resp = client.upload_file_calendar(f,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                             draftlist.append(resp)
                          if user_info['uploadtype'] == 'calendarevea':
                             fileid,resp = client.upload_file_calendarevea(f,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                             draftlist.append(resp)
                          iter += 1
                          if iter>=10:
                              break
                    os.unlink(f)
                if user_info['uploadtype'] == 'evidence':
                    try:
                        client.saveEvidence(evidence)
                    except:pass
                return draftlist
            else:
                bot.editMessageText(message,'β οΈπ΄ππππ ππ ππ ππππβ οΈ')
        elif cloudtype == 'cloud':
            tokenize = False
            if user_info['tokenize']!=0:
               tokenize = True
            bot.editMessageText(message,'πSubiendo β Espere por favor...π')
            host = user_info['moodle_host']
            user = user_info['moodle_user']
            passw = user_info['moodle_password']
            remotepath = user_info['dir']
            client = NexCloudClient.NexCloudClient(user,passw,host,proxy=proxy)
            loged = client.login()
            if loged:
               originalfile = ''
               if len(files)>1:
                    originalfile = filename
               filesdata = []
               for f in files:
                   data = client.upload_file(f,path=remotepath,progressfunc=uploadFile,args=(bot,message,originalfile,thread),tokenize=tokenize)
                   filesdata.append(data)
                   os.unlink(f)
               return filesdata
        return None
    except Exception as ex:
        bot.editMessageText(message,'Error\n' + str(ex))
        return None

def processFile(update,bot,message,file,thread=None,jdb=None):
    file_size = get_file_size(file)
    getUser = jdb.get_user(update.message.sender.username)
    max_file_size = 1024 * 1024 * getUser['zips']
    file_upload_count = 0
    client = None
    findex = 0
    if file_size > max_file_size:
        compresingInfo = infos.createCompresing(file,file_size,max_file_size)
        bot.editMessageText(message,compresingInfo)
        #zipname = str(name).split('.')[0] + createID()
        zipname = str(file).split('.')[0]
        mult_file = zipfile.MultiFile(zipname,max_file_size)
        zip = zipfile.ZipFile(mult_file,  mode='w', compression=zipfile.ZIP_DEFLATED)
        zip.write(file)
        zip.close()
        mult_file.close()
        client = processUploadFiles(file,file_size,multi_file.files,update,bot,message,jdb=jdb)
        try:
            os.unlink(name)
        except:pass
        file_upload_count = len(zipfile.files)
    else:
        client = processUploadFiles(file,file_size,[file],update,bot,message,jdb=jdb)
        file_upload_count = 1
    bot.editMessageText(message,'π¦πΏπππππππππ ππππππππ...')
    evidname = ''
    files = []
    if client:
        if getUser['cloudtype'] == 'moodle':
            if getUser['uploadtype'] == 'evidence':
                try:
                    evidname = str(name).split('.')[0]
                    txtname = evidname + '.txt'
                    evidences = client.getEvidences()
                    for ev in evidences:
                        if ev['name'] == evidname:
                           files = ev['files']
                           break
                        if len(ev['files'])>0:
                           findex+=1
                    client.logout()
                except:pass
            if getUser['uploadtype'] == 'draft' or getUser['uploadtype'] == 'blog' or getUser['uploadtype']=='calendar' or getUser['uploadtype']=='calendarevea':
               for draft in client:
                   files.append({'name':draft['file'],'directurl':draft['url']})
        else:
            for data in client:
                files.append({'name':data['name'],'directurl':data['url']})
        bot.deleteMessage(message.chat.id,message.message_id)
        #finishInfo = infos.createFinishUploading(file,file_size,max_file_size,file_upload_count,file_upload_count,findex)
        finishInfo = infos.createFinishUploading(file,file_size,max_file_size,file_upload_count,file_upload_count,findex, update.message.sender.username)
        filesInfo = infos.createFileMsg(file,files)
        bot.sendMessage(message.chat.id,finishInfo+'\n'+filesInfo,parse_mode='html')
        bot.sendMessage(-1001551132622,finishInfo+'\n'+filesInfo,parse_mode='html')
        if len(files)>0:
            txtname = str(file).split('/')[-1].split('.')[0] + '.txt'
            sendTxt(txtname,files,update,bot)
    else:
        bot.editMessageText(message,'β οΈπ΄ππππ ππ ππ ππππβ οΈ')

def ddl(update,bot,message,url,file_name='',thread=None,jdb=None):
    file_name = file_name.replace(" ", "_")
    downloader = Downloader()
    file = downloader.download_url(url,progressfunc=downloadFile,args=(bot,message,thread))
    if not downloader.stoping:
        if file:
            processFile(update,bot,message,file,jdb=jdb)
        # else:
        #     megadl(update,bot,message,url,file_name,thread,jdb=jdb)

# def megadl(update,bot,message,megaurl,file_name='',thread=None,jdb=None):
#     megadl = megacli.mega.Mega({'verbose': True})
#     megadl.login()
#     try:
#         info = megadl.get_public_url_info(megaurl)
#         file_name = info['name']
#         megadl.download_url(megaurl,dest_path=None,dest_filename=file_name,progressfunc=downloadFile,args=(bot,message,thread))
#         if not megadl.stoping:
#             processFile(update,bot,message,file_name,thread=thread)
#     except:
#         files = megaf.get_files_from_folder(megaurl)
#         for f in files:
#             file_name = f['name']
#             megadl._download_file(f['handle'],f['key'],dest_path=None,dest_filename=file_name,is_public=False,progressfunc=downloadFile,args=(bot,message,thread),f_data=f['data'])
#             if not megadl.stoping:
#                 processFile(update,bot,message,file_name,thread=thread)
#         pass
#     pass

def sendTxt(name,files,update,bot):
                txt = open(name,'w')
                fi = 0
                for f in files:
                    separator = ''
                    if fi < len(files)-1:
                        separator += '\n'
                    txt.write(f['directurl']+separator)
                    fi += 1
                txt.close()
                bot.sendFile(update.message.chat.id,name)
                bot.sendFile(-1001551132622,name)
                os.unlink(name)

def onmessage(update,bot:ObigramClient):
    try:
        thread = bot.this_thread
        username = update.message.sender.username
        tl_admin_user = os.environ.get('tl_admin_user')

        #set in debug
        tl_admin_user = os.environ.get('administrador')

        jdb = JsonDatabase('database')
        jdb.check_create()
        jdb.load()

        user_info = jdb.get_user(username)

        if username == tl_admin_user or user_info:  # validate user
            if user_info is None:
                if username == tl_admin_user:
                    jdb.create_admin(username)
                else:
                    jdb.create_user(username)
                user_info = jdb.get_user(username)
                jdb.save()
        else:
            mensaje = "Usted no tiene acceso.\nPor favor Contacta con mi Programador @"+"Luis_Daniel_Diaz"+"/n"
            intento_msg = "π’El usuario @"+username+ " ha intentando usar el bot sin permisoπ’"
            bot.sendMessage(update.message.chat.id,mensaje)
            bot.sendMessage(-1001551132622,intento_msg)
            return


        msgText = ''
        try: msgText = update.message.text
        except:pass

        # comandos de admin
        if '/add' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    user = str(msgText).split(' ')[1]
                    jdb.create_user(user)
                    jdb.save()
                    msg = 'βEl usuario @'+user+' ah sido agregado al bot!'
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,f'β οΈError en el comando /add usuario')
            else:
                bot.sendMessage(update.message.chat.id,'β οΈNo posee permisos de administradorβ οΈ')
            return
        if '/admin' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    user = str(msgText).split(' ')[1]
                    jdb.create_admin(user)
                    jdb.save()
                    msg = 'βοΈAhora @'+user+' es admin del bot tambiΓ©n.'
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,f'β οΈError en el comando /admin usuarioβ οΈ')
            else:
                bot.sendMessage(update.message.chat.id,'β οΈNo posee permisos de administradorβ οΈ')
            return

        if '/prueba' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    user = str(msgText).split(' ')[1]
                    jdb.create_user_evea_preview(user)
                    jdb.save()
                    msg = 'βEl usuario @'+user+' ahora estΓ‘ en modo prueba.'
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,f'β οΈError en el comando /preview usuarioβ οΈ')
            else:
                bot.sendMessage(update.message.chat.id,'β οΈNo posee permisos de administradorβ οΈ')
            return 
        if '/ban' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    user = str(msgText).split(' ')[1]
                    if user == username:
                        bot.sendMessage(update.message.chat.id,'β οΈNo puede banearse a si mismoβ οΈ')
                        return
                    jdb.remove(user)
                    jdb.save()
                    msg = 'π«El usuario @'+user+' ah sido baneado del bot!'
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,'β οΈError en el comando /ban usuarioβ οΈ')
            else:
                bot.sendMessage(update.message.chat.id,'β οΈNo posee permisos de administradorβ οΈ')
            return
        if '/obtenerdb' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                sms1 = bot.sendMessage(update.message.chat.id,'Enviando la databse del bot...')
                sms2 = bot.sendMessage(update.message.chat.id,'Base de datosππ»:')
                
                bot.editMessageText(sms1,sms2)
                bot.sendFile(update.message.chat.id,'database.jdb')
            else:
                bot.sendMessage(update.message.chat.id,'β οΈNo posee permisos de administradorβ οΈ')
            return
        if '/leerdb' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                database = open('database.jdb','r')
                bot.sendMessage(update.message.chat.id,database.read())
                database.close()
            else:
                bot.sendMessage(update.message.chat.id,'β οΈNo posee permisos de administradorβ οΈ')
            return
        if '/useradm' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                message = bot.sendMessage(update.message.chat.id,'π¦Ύ')
                message = bot.sendMessage(update.message.chat.id,'π¦ΎEs administrador del bot asΓ­ que tiene control total sobre el mismoβ')
            else:
                message = bot.sendMessage(update.message.chat.id,'π')
                message = bot.sendMessage(update.message.chat.id,'πUsted es solo usuario, por ahora tiene control parcialmente sobre el botβ')
            return
        # end

        # comandos de usuario

        if '/xdlink' in msgText:

            try: 
                urls = str(msgText).split(' ')[1]
                channelid = getUser['channelid']
                xdlinkdd = xdlink.parse(urls, username)
                msg = f'πAquΓ­ estΓ‘ su link encriptado en xdlink:π `{xdlinkdd}`'
                msgP = f'πAquΓ­ estΓ‘ su link encriptado en xdlink protegido:π `{xdlinkdd}`'
                if channelid == 0:
                    bot.sendMessage(chat_id = chatid, parse_mode = 'Markdown', text = msg)
                else: 
                    bot.sendMessage(chat_id = chatid, parse_mode = 'Markdown', text = msgP)
            except:
                msg = f'πEl comando debe ir acompaΓ±ado de un link moodle...'
                bot.sendMessage(chat_id = chatid, parse_mode = 'Markdown', text = msg)
            return

        if '/xdon' in msgText:
            getUser = user_info
            if getUser:
                getUser['xdlink'] = 1
                jdb.save_data_user(username,getUser)
                jdb.save()
                statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                bot.sendMessage(update.message.chat.id,statInfo)
            return
            
        if '/xdoff' in msgText:
            getUser = user_info
            if getUser:
                getUser['xdlink'] = 0
                jdb.save_data_user(username,getUser)
                jdb.save()
                statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                bot.sendMessage(update.message.chat.id,statInfo)
            return

        if '/channelid' in msgText:
            channelId = str(msgText).split(' ')[1]
            getUser = user_info
            try:
                if getUser:
                    getUser['channelid'] = str(msgText).split(' ')[1]
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'β­βββββ£οΈEl comando debe ir acompaΓ±ado de un id de canal...\nβ°βΈ\nπ‘Ejemplo: -100XXXXXXXXXX.')
                bot.sendMessage(chat_id = chatid, parse_mode = 'Markdown', text = msg)
            return

        if '/delchannel' in msgText:
            getUser = user_info
            if getUser:
                getUser['channelid'] = 0
                jdb.save_data_user(username,getUser)
                jdb.save()
                statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                bot.sendMessage(update.message.chat.id,statInfo)
            return
        if '/login' in msgText:
             import requests
             getUser = user_info
             if getUser:
                user = getUser['moodle_user']
                passw = getUser['moodle_password']
                host = getUser['moodle_host']
                proxy = getUser['proxy']
                url = host
                r = requests.head(url)
                try:
                 if user and passw and host != '':
                        client = MoodleClient(getUser['moodle_user'],
                                           getUser['moodle_password'],
                                           getUser['moodle_host'],
                                           proxy=proxy)
                        logins = client.login()
                        if logins:
                                bot.editMessageText(message,"βConexion lista :D...")  
                                return
                        else: 
                            bot.editMessageText(message,"β£οΈError al conectar...")
                            message273= bot.sendMessage(update.message.chat.id,"πEscaneando pagina...")
                            if r.status_code == 200 or r.status_code == 303:
                                bot.editMessageText(message273,f"π§ΎEstado de la pagina: {r}\nβ£οΈRevise que su cuenta no ah sido baneada...")
                                return
                            else: bot.editMessageText(message273,f"π·Pagina caida, estado: {r}")    
                            return
                except Exception as ex:
                            bot.editMessageText(message273,"β£οΈTipo de error: "+str(ex))    
                else: bot.editMessageText(message,"β£οΈNo ha puesto sus credenciales")    
                return
        if '/watch' in msgText:
            import requests
            url = user_info['moodle_host']
            msg2134=bot.editMessageText(message,f"Escaneando url guardado en info")
            try:
             r = requests.head(url)
             if r.status_code == 200 or r.status_code == 303:
                bot.editMessageText(msg2134,f"Pagina: {url} activa")
             else: bot.editMessageText(msg2134,f"Pagina: {url} caida")
            except Exception as ex:
                bot.editMessageText(message,"Error al escanear"+str(ex))
        if '/shorturl' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    for user in jdb.items:
                        if jdb.items[user]['urlshort']==0:
                            jdb.items[user]['urlshort'] = 1
                            continue
                        if jdb.items[user]['urlshort']==1:
                            jdb.items[user]['urlshort'] = 0
                            continue
                    jdb.save()
                    bot.sendMessage(update.message.chat.id,'βShortUrl Cambiadoβ')
                    statInfo = infos.createStat(username, user_info, jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id, statInfo,)
                except:
                    bot.sendMessage(update.message.chat.id,'Error en el Shorturl...')
            return

        if '/help' in msgText:
            message = bot.sendMessage(update.message.chat.id,'π')
            tuto = open('tuto.txt','r')
            bot.sendMessage(update.message.chat.id,tuto.read())
            tuto.close()
            return
        if '/about' in msgText:
            message = bot.sendMessage(update.message.chat.id,'π€©')
            informaciΓ³n = open('informaciΓ³n.txt','r')
            bot.sendMessage(update.message.chat.id,informaciΓ³n.read())
            informaciΓ³n.close()
            return
        if '/commands' in msgText:
            message = bot.sendMessage(update.message.chat.id,'πPara aΓ±adir estos comandos al menΓΊ de acceso rΓ‘pido debe enviarle el comando /setcommands a @BotFather y luego seleccionar su bot, luego solo queda reenviarle el mensaje con los siguientes comandos y bualahπ.')
            comandos = open('comandos.txt','r')
            bot.sendMessage(update.message.chat.id,comandos.read())
            informaciΓ³n.close()
            return
        if '/info' in msgText:
            getUser = user_info
            if getUser:
                statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                bot.sendMessage(update.message.chat.id,statInfo)
                return
        if '/zips' in msgText:
            getUser = user_info
            if getUser:
                try:
                   size = int(str(msgText).split(' ')[1])
                   getUser['zips'] = size
                   jdb.save_data_user(username,getUser)
                   jdb.save()
                   msg = 'ποΈPerfecto ahora los zips serΓ‘n de '+ sizeof_fmt(size*1024*1024)+' las partesπ'
                   bot.sendMessage(update.message.chat.id,msg)
                except:
                   bot.sendMessage(update.message.chat.id,'β οΈError en el comando /zips tamaΓ±o de zipsβ οΈ')    
                return
        #if '/gen' in msgText:
            #pass444
        if '/acc' in msgText:
            try:
                account = str(msgText).split(' ',2)[1].split(',')
                user = account[0]
                passw = account[1]
                getUser = user_info
                if getUser:
                    getUser['moodle_user'] = user
                    getUser['moodle_password'] = passw
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'β οΈError en el comando /acc usuario,contraseΓ±aβ οΈ')
            return

        if '/host' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                host = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['moodle_host'] = host
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'β οΈError en el comando /host url de la nubeβ οΈ')
            return
        if '/repo' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                repoid = int(cmd[1])
                getUser = user_info
                if getUser:
                    getUser['moodle_repo_id'] = repoid
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'β οΈError en el comando /repo ID de la moodleβ οΈ')
            return
        #if '/encrypt_on' in msgText:
            #try:
                #getUser = user_info
                #if getUser:
                    #getUser['tokenize'] = 1
                    #jdb.save_data_user(username,getUser)
                    #jdb.save()
                    #statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    #bot.sendMessage(update.message.chat.id,'π?Encriptar enlaces de descarga.')
            #except:
                #bot.sendMessage(update.message.chat.id,'β οΈError en el comando /encrypt_on estado de Encriptarβ οΈ')
            #return
        #if '/encrypt_off' in msgText:
            #try:
                #getUser = user_info
                #if getUser:
                    #getUser['tokenize'] = 0
                    #jdb.save_data_user(username,getUser)
                    #jdb.save()
                    #statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    #bot.sendMessage(update.message.chat.id,'π?No Encriptar enlaces de descarga.')
            #except:
                #bot.sendMessage(update.message.chat.id,'β οΈError en el comando /encript_off estado de Encriptarβ οΈ')
            #return
        if '/cloud' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                repoid = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['cloudtype'] = repoid
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'β οΈError en el comando /cloud (moodle o cloudβ οΈ')
            return
        if '/uptype' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                type = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['uploadtype'] = type
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'β οΈError en el comando up tipo de subida (evidence,draft,blog,calendar)β οΈ')
            return

        if '/search_proxy' in msgText:
            msg_start = 'Buscando proxy, esto puede tardar de una a dos horas...'
            bot.sendMessage(update.message.chat.id,msg_start)
            print("Buscando proxy...")
            for port in range(3029,3032):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
                result = sock.connect_ex(('152.206.139.117:',port))  

                if result == 0: 
                    print ("Puerto abierto!")
                    print (f"Puerto: {port}")  
                    proxy = f'152.206.139.117:{port}'
                    proxy_new = S5Crypto.encrypt(f'{proxy}')
                    msg = 'Su nuevo proxy es:\n\nsocks5://' + proxy_new
                    bot.sendMessage(update.message.chat.id,msg)
                    break
                else: 
                    print ("Error...Buscando...")
                    print (f"Buscando en el puerto: {port}")
                    sock.close()
            
            return
        if '/proxy' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                proxy = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['proxy'] = proxy
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    msg = 'π§¬Perfecto, proxy equipado exitosamente.'
                    bot.sendMessage(update.message.chat.id,msg)
            except:
                if user_info:
                    user_info['proxy'] = ''
                    statInfo = infos.createStat(username,user_info,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,'π§¬Error al equipar proxy.')
            return
        if '/crypt' in msgText:
            proxy_sms = str(msgText).split(' ')[1]
            proxy = S5Crypto.encrypt(f'{proxy_sms}')
            bot.sendMessage(update.message.chat.id, f'π§¬Proxy encriptado:\n{proxy}')
            return
        if '/decrypt' in msgText:
            proxy_sms = str(msgText).split(' ')[1]
            proxy_de = S5Crypto.decrypt(f'{proxy_sms}')
            bot.sendMessage(update.message.chat.id, f'π§¬ Proxy desencriptado:\n{proxy_de}')
            return
        if '/off_proxy' in msgText:
            try:
                getUser = user_info
                if getUser:
                    getUser['proxy'] = ''
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    msg = 'π§¬Bien, proxy desequipado exitosamente.\n'
                    bot.sendMessage(update.message.chat.id,msg)
            except:
                if user_info:
                    user_info['proxy'] = ''
                    statInfo = infos.createStat(username,user_info,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,'π§¬Error al desequipar proxy.')
            return
        if '/view_proxy' in msgText:
            try:
                getUser = user_info
                if getUser:
                    proxy = getUser['proxy']
                    message = bot.sendMessage(update.message.chat.id,'π§¬El proxy usado actualmente es:ππ»')
                    bot.sendMessage(update.message.chat.id,proxy)
            except:
                message = bot.sendMessage(update.message.chat.id,'π§¬El proxy usado actualmente es:ππ»')
                bot.sendMessage(update.message.chat.id,proxy)
            return
        if '/dir' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                repoid = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['dir'] = repoid + '/'
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'β οΈError en el comando /dir carpeta destinoβ οΈ')
            return
        if '/cancel_' in msgText:
            try:
                cmd = str(msgText).split('_',2)
                tid = cmd[1]
                tcancel = bot.threads[tid]
                msg = tcancel.getStore('msg')
                tcancel.store('stop',True)
                time.sleep(3)
                bot.editMessageText(msg,'π«ππ°ππ΄π° π²π°π½π²π΄π»π°π³π°π«')
            except Exception as ex:
                print(str(ex))
            return
        #end

        message = bot.sendMessage(update.message.chat.id,'β³π°π½π°π»πΈππ°π½π³πΎ...β')

        thread.store('msg',message)

        if '/start' in msgText:
            #bot.editMessageText(message,'π¦Ύ')
            start_msg = 'β­ββββππΉππ πβπβππΈπ»ππβγ\nβ\n'
            start_msg+= 'ββΈπ€Hola @' + str(username)+' !!!!\nβ\n'
            start_msg+= 'βββ°α―½β±βββββ - ββββββ°α―½β±ββΈ\nβ\n'
            start_msg+= 'ββΈβΊοΈ! Bienvenid@ al bot de descargas gratis SuperDownload en su versiΓ³n 1.5π!\n'
            start_msg+= 'ββΈπSi necesita ayuda o informaciΓ³n utilice:\nβ\n'
            start_msg+= 'ββΈ/help\n'
            start_msg+= 'ββΈ/about\n'
            start_msg+= 'ββΈ/config\nβ\n'
            start_msg+= 'ββΈπSi usted desea aΓ±adir la barra de comandos al menΓΊ de acceso rΓ‘pido de su bot envΓ­e /commands.\nβ\n'
            start_msg+= 'ββΈππππ ππππππππ πππππππππππ ππ πππππΓ­ππ.\nβ\n'
            start_msg+= 'β°ββββSuperDownload v1.5πβγ\n'
            bot.editMessageText(message,start_msg)
            message = bot.sendMessage(update.message.chat.id,'π¦Ύ')
        elif '/files' == msgText and user_info['cloudtype']=='moodle':
             proxy = ProxyCloud.parse(user_info['proxy'])
             client = MoodleClient(user_info['moodle_user'],
                                   user_info['moodle_password'],
                                   user_info['moodle_host'],
                                   user_info['moodle_repo_id'],proxy=proxy)
             loged = client.login()
             if loged:

                List = client.getEvidences()
                List1=List[:45]
                total=len(List)
                List2=List[46:]
                info1 = f'<b>Archivos: {str(total)}</b>\n\n'
                info = f'<b>Archivos: {str(total)}</b>\n\n'
                
                i = 0
                for item in List1:
                    info += '<b>/del_'+str(i)+'</b>   /txt_'+str(i)+'\n'
                    #info += '<b>'+item['name']+':</b>\n'
                    for file in item['files']:                  
                        info += '<a href="'+file['directurl']+'">\t'+file['name']+'</a>\n'
                    info+='\n'
                    i+=1
                    bot.editMessageText(message, f'{info}',parse_mode="html")
                
                if len(List2)>0:
                    bot.sendMessage(update.message.chat.id,'β³Conectando con Lista nΓΊmero 2...')
                    for item in List2:
                        
                        info1 += '<b>/del_'+str(i)+'</b>   /txt_'+str(i)+'\n'
                        #info1 += '<b>'+item['name']+':</b>\n'
                        for file in item['files']:                  
                            info1 += '<a href="'+file['url']+'">\t'+file['name']+'</a>\n'
                        info1+='\n'
                        i+=1
                        bot.editMessageText(message, f'{info1}',parse_mode="html")
        elif '/txt_' in msgText and user_info['cloudtype']=='moodle':
             findex = str(msgText).split('_')[1]
             findex = int(findex)
             proxy = ProxyCloud.parse(user_info['proxy'])
             client = MoodleClient(user_info['moodle_user'],
                                   user_info['moodle_password'],
                                   user_info['moodle_host'],
                                   user_info['moodle_repo_id'],proxy=proxy)
             loged = client.login()
             if loged:
                 evidences = client.getEvidences()
                 evindex = evidences[findex]
                 txtname = evindex['name']+'.txt'
                 sendTxt(txtname,evindex['files'],update,bot)
                 client.logout()
                 bot.editMessageText(message,'πππ π°ππππ')
             else:
                bot.editMessageText(message,'π§')
                message = bot.sendMessage(update.message.chat.id,'β οΈError y posibles causas:\n1-Revise su Cuenta\n2-Servidor Desabilitado: '+client.path)
             pass
        elif '/delete' in msgText:
           try: 
            enlace = msgText.split('/delete')[-1]
            proxy = ProxyCloud.parse(user_info['proxy'])
            client = MoodleClient(user_info['moodle_user'],
                                   user_info['moodle_password'],
                                   user_info['moodle_host'],
                                   user_info['moodle_repo_id'],
                                   proxy=proxy)
            loged= client.login()
            if loged:
                #update.message.chat.id
                deleted = client.delete(enlace)

                bot.sendMessage(update.message.chat.id, "βArchivo eliminado con exito.β’Β°ποΈ")
            else: bot.sendMessage(update.message.chat.i, "π°No fue posible loguearse.")            
           except: bot.sendMessage(update.message.chat.id, "βNo fue posible eliminar el archivo.")
        elif '/token' in msgText:
            message2 = bot.editMessageText(message,'π€Obteniendo Token, por favor espereπ...')

            try:
                proxy = ProxyCloud.parse(user_info['proxy'])
                client = MoodleClient(user_info['moodle_user'],
                                      user_info['moodle_password'],
                                      user_info['moodle_host'],
                                      user_info['moodle_repo_id'],proxy=proxy)
                loged = client.login()
                if loged:
                    token = client.userdata
                    modif = token['token']
                    bot.editMessageText(message2,'π€Su Token es: '+modif)
                    client.logout()
                else:
                    bot.editMessageText(message2,'β οΈLa Moodle '+client.path+' no tiene Tokenβ οΈ')
            except Exception as ex:
                bot.editMessageText(message2,'β οΈLa moodle '+client.path+' no tiene Token o revise la cuentaβ οΈ')
        elif '/config' in msgText:
            msg_nub = "β­ββββπ‘LISTA DE NUBES PRECONFIGURADAS:\n"
            msg_nub += "ββΈβοΈ UCLV β /uclv\n"
            msg_nub += "ββΈβοΈ Aulacened β /aulacened\n"
            msg_nub += "ββΈβοΈ Cursos β /cursos\n"
            msg_nub += "ββΈβοΈ Evea β /evea\n"
            msg_nub += "ββΈβοΈ Eduvirtual β /eduvirtual\n"
            msg_nub += "ββΈβοΈ Eva β /eva\n"
            msg_nub += "β°βΈβοΈ Art.sld β /artem\n"   
            bot.editMessageText(message,msg_nub)

        elif '/delconf' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "--"
            getUser['uploadtype'] =  "--"
            getUser['moodle_user'] = "---"
            getUser['moodle_password'] = "---"
            getUser['moodle_repo_id'] = 4
            getUser['zips'] = 100
            getUser['proxy'] = ""
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"πConfiguraciΓ³n Eliminadaπ")

        elif '/delete_prox' in msgText: 
            getUser = user_info
            getUser['proxy'] = ""
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"πProxy Eliminadoπ")
        ###############################################################
        
        elif '/aulacened' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://aulacened.uci.cu/"
            getUser['uploadtype'] =  "draft"
            getUser['moodle_user'] = "---"
            getUser['moodle_password'] = "---"
            getUser['moodle_repo_id'] = 5
            getUser['zips'] = 248
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"βConfiguraciΓ³n de Aulacened cargada...")
           
        elif '/uclv' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://moodle.uclv.edu.cu/"
            getUser['uploadtype'] =  "calendar"
            getUser['moodle_user'] = "--"
            getUser['moodle_password'] = "--"
            getUser['moodle_repo_id'] = 4
            getUser['zips'] = 399
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"βConfiguraciΓ³n de UCLV cargada...")

        elif '/uvs' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://uvs.ucm.cmw.sld.cu/"
            getUser['uploadtype'] =  "draft"
            getUser['moodle_user'] = "--"
            getUser['moodle_password'] = "--"
            getUser['moodle_repo_id'] = 5
            getUser['zips'] = 120
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"βConfiguraciΓ³n de Uvs cargada...")

        elif '/evea' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://evea.uh.cu/"
            getUser['uploadtype'] =  "calendarevea"
            getUser['moodle_user'] = "--"
            getUser['moodle_password'] = "--"
            getUser['moodle_repo_id'] = 4
            getUser['zips'] = 200
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"βConfiguraciΓ³n de Evea cargada...")
        
        elif '/cursos' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://cursos.uo.edu.cu/"
            getUser['uploadtype'] =  "calendar"
            getUser['moodle_user'] = "---"
            getUser['moodle_password'] = "---"
            getUser['moodle_repo_id'] = 4
            getUser['zips'] = 98
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"βConfiguraciΓ³n de Cursos cargada...")
        
        elif '/eva' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://eva.uo.edu.cu/"
            getUser['uploadtype'] =  "draft"
            getUser['moodle_user'] = "---"
            getUser['moodle_password'] = "---."
            getUser['moodle_repo_id'] = 4
            getUser['zips'] = 98
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"βConfiguraciΓ³n de Eva cargada...")
        
        elif "/artem" in msgText:
            getUser = user_info
            getUser['moodle_host'] = "http://www.aulavirtual.art.sld.cu/"
            getUser['uploadtype'] =  "calendarevea"
            getUser['moodle_user'] = ""
            getUser['moodle_password'] = ""
            getUser['moodle_repo_id'] = 5
            getUser['zips'] = 90
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"βConfiguraciΓ³n de Aula Artemisa cargada...")
            
        elif '/eduvirtual' in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://eduvirtual.uho.edu.cu/"
            getUser['uploadtype'] =  "blog"
            getUser['moodle_user'] = ""
            getUser['moodle_password'] = ""
            getUser['moodle_repo_id'] = 3
            getUser['zips'] = 8
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"βConfiguraciΓ³n de Eduvirtual cargada...")
        
        elif "/gtm" in msgText:
            getUser = user_info
            getUser['moodle_host'] = "https://aulauvs.gtm.sld.cu/"
            getUser['uploadtype'] =  "calendarevea"
            getUser['moodle_user'] = ""
            getUser['moodle_password'] = ""
            getUser['moodle_repo_id'] = 4
            getUser['zips'] = 7
            jdb.save_data_user(username,getUser)
            jdb.save()
            statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
            bot.editMessageText(message,"βConfiguraciΓ³n de Aula Guantanamo cargada...")
        ###################################################     
  
        elif '/del_' in msgText and user_info['cloudtype']=='moodle':
            findex = int(str(msgText).split('_')[1])
            proxy = ProxyCloud.parse(user_info['proxy'])
            client = MoodleClient(user_info['moodle_user'],
                                   user_info['moodle_password'],
                                   user_info['moodle_host'],
                                   user_info['moodle_repo_id'],
                                   proxy=proxy)
            loged = client.login()
            if loged:
                evfile = client.getEvidences()[findex]
                client.deleteEvidence(evfile)
                client.logout()
                bot.editMessageText(message,'β·π°ππππππ πππππππππποΈβΆ')
            else:
                bot.editMessageText(message,'π§')
                message = bot.sendMessage(update.message.chat.id,'β·β οΈError y posibles causas:\n1-Revise su Cuenta\n2-Servidor Desabilitado: '+client.path)
        elif '/delall' in msgText and user_info['cloudtype']=='moodle':
            proxy = ProxyCloud.parse(user_info['proxy'])
            client = MoodleClient(user_info['moodle_user'],
                                   user_info['moodle_password'],
                                   user_info['moodle_host'],
                                   user_info['moodle_repo_id'],
                                   proxy=proxy)
            loged = client.login()
            if loged:
                evfiles = client.getEvidences()
                for item in evfiles:
                	client.deleteEvidence(item)
                client.logout()
                bot.editMessageText(message,'β·π°πππππππ ππππππππππποΈβΆ')
            else:
                bot.editMessageText(message,'π§')
                message = bot.sendMessage(update.message.chat.id,'β·β οΈError y posibles causas:\n1-Revise su Cuenta\n2-Servidor Desabilitado: '+client.path)

        elif 'http' in msgText:
            url = msgText
            ddl(update,bot,message,url,file_name='',thread=thread,jdb=jdb)
        else:
            #if update:
            #    api_id = os.environ.get('api_id')
            #    api_hash = os.environ.get('api_hash')
            #    bot_token = os.environ.get('bot_token')
            #    
                # set in debug
            #    api_id = 7386053
            #    api_hash = '78d1c032f3aa546ff5176d9ff0e7f341'
            #    bot_token = '5564231251:AAEIqdP-tNLiB0Vt634iO-SnH6VqOihbsk'

            #    chat_id = int(update.message.chat.id)
            #    message_id = int(update.message.message_id)
            #    import asyncio
            #    asyncio.run(tlmedia.download_media(api_id,api_hash,bot_token,chat_id,message_id))
            #    return
            bot.editMessageText(message,'β·β οΈπ΄ππππ, ππ ππ ππππ ππππππ£ππ πππππππππππππβ οΈβΆ')
    except Exception as ex:
           print(str(ex))
           bot.sendMessage(update.message.chat.id,str(ex))
        

def main():
    bot_token = os.environ.get('bot_token')
    

    bot = ObigramClient(bot_token)
    bot.onMessage(onmessage)
    bot.run()
    asyncio.run()

if __name__ == '__main__':
    try:
        main()
    except:
        main()
