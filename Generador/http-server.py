#!/bin/bash

IVAR="/etc/http-instas"
# FUNCIÓN PARA DETERMINAR IP
remover_key_usada () {
local DIR="/etc/http-shell"
i=0
[[ -z $(ls $DIR|grep -v "ERROR-KEY") ]] && return
for arqs in `ls $DIR|grep -v "ERROR-KEY"|grep -v ".name"`; do
	
 if [[ -e ${DIR}/${arqs}/used.date ]]; then #KEY USADA
  if [[ $(ls -l -c ${DIR}/${arqs}/used.date|cut -d' ' -f7) != $(date|cut -d' ' -f3) ]]; then
  rm -rf ${DIR}/${arqs}*
  fi
 fi
let i++
done
}
fun_ip () {
if [[ ! -e /etc/MEU_IP ]]; then
local MIP=$(ip addr | grep 'inet' | grep -v inet6 | grep -vE '127\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | grep -o -E '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | head -1)
local MIP2=$(wget -qO- ipv4.icanhazip.com)
[[ "$MIP" != "$MIP2" ]] && IP="$MIP2" || IP="$MIP"
echo "$IP" > /etc/MEU_IP
echo "$IP"
else
echo "$(cat /etc/MEU_IP)"
fi
}

#OFUSCAR
ofus () {
unset txtofus
number=$(expr length $1)
for((i=1; i<$number+1; i++)); do
txt[$i]=$(echo "$1" | cut -b $i)
case ${txt[$i]} in
".") txt[$i]="+";;
"+") txt[$i]=".";;
"1") txt[$i]="@";;
"@") txt[$i]="1";;
"2") txt[$i]="?";;
"?") txt[$i]="2";;
"3") txt[$i]="%";;
"%") txt[$i]="3";;
"/") txt[$i]="K";;
"K") txt[$i]="/";;
esac
txtofus+="${txt[$i]}"
done
echo "$txtofus" | rev
}


# BUCLE PARA EJECUCIÓN DEL PROGRAMA
listen_fun () {
local PORTA="8888" && local PROGRAMA="/bin/http-server.sh"
while true; do nc.traditional -l -p "$PORTA" -e "$PROGRAMA"; done
}
# SERVIDOR EJECUTABLE
server_fun () {
DIR="/etc/http-shell" #DIRECTORIO DE LLAVES ALMACENADAS
if [[ ! -d $DIR ]]; then mkdir $DIR; fi
read URL
KEY=$(echo $URL|cut -d' ' -f2|cut -d'/' -f2) && [[ ! $KEY ]] && KEY="ERROR" #KEY
ARQ=$(echo $URL|cut -d' ' -f2|cut -d'/' -f3)  && [[ ! $ARQ ]] && ARQ="ERROR" #LISTA DE INSTALACIÓN
USRIP=$(echo $URL|cut -d' ' -f2|cut -d'/' -f4) && [[ ! $USRIP ]] && USRIP="ERROR" #IP DE USUARIO
SO=$(echo $URL|cut -d' ' -f2|cut -d'/' -f5) && [[ ! $SO ]] && SO="ERROR DE SISTEMA OPERATIVO"
UUID=$(echo $URL|cut -d' ' -f2|cut -d'/' -f6) && [[ ! $UUID ]] && UUID="SERIAL QR NO RECIBIDO"
echo "KEY: $KEY" >&2
echo "LISTA: $ARQ" >&2
echo "IP: $USRIP" >&2
echo "SO: $SO" >&2
echo "UUID: $UUID" >&2
DIRETORIOKEY="$DIR/$KEY" # DIRECTORIO CLAVE
LISTADEARQUIVOS="$DIRETORIOKEY/$ARQ" # LISTA DE ARCHIVOS
if [[ -d "$DIRETORIOKEY" ]]; then #COMPROBANDO SI LA LLAVE EXISTE
  if [[ -e "$DIRETORIOKEY/$ARQ" ]]; then #COMPROBAR LA LISTA DE ARCHIVOS
  #ENVIA LISTA DE DESCARGAS
  FILE="$DIRETORIOKEY/$ARQ" 
  STATUS_NUMBER="200"
  STATUS_NAME="Found"
  ENV_ARQ="True"
  fi
  if [[ -e "$DIRETORIOKEY/FERRAMENTA" ]]; then #VERIFICA SI LA CLAVE Y LA HERRAMIENTA EXISTEN
   if [[ ${USRIP} != "ERROR" ]]; then #SI ES UNA HERRAMIENTA, LA IP NO DEBE SER ENVIADA
    FILE="${DIR}/ERROR-KEY"
    echo "CLAVE DE HERRAMIENTA!" > ${FILE}
    ENV_ARQ="False"
   fi
 else
   if [[ ${USRIP} = "ERROR" ]]; then #VERIFICA SI ES UNA INSTALACIÓN, LA IP DEBE SER ENVIADA
    FILE="${DIR}/ERROR-KEY"
    echo "CLAVE DE INSTALACIÓN!" > ${FILE}
    ENV_ARQ="False"
   fi
 fi
else
# KEY INVALIDA
  FILE="${DIR}/ERROR-KEY"
  echo "KEY INVALIDA!" > ${FILE}
  STATUS_NUMBER="200"
  STATUS_NAME="Found"
  ENV_ARQ="False"
fi
#ENVIAR DATOS AL USUARIO
cat << EOF
HTTP/1.1 $STATUS_NUMBER - $STATUS_NAME
Date: $(date)
Server: ShellHTTP
Content-Length: $(wc --bytes "$FILE" | cut -d " " -f1)
Connection: close
Content-Type: text/html; charset=utf-8
$(cat "$FILE")
EOF
#FINALIZAR EL ENVÍO
if [[ $ENV_ARQ != "True" ]]; then exit; fi #FINALIZAR SOLICITUD SI NO ENVÍA ARCHIVOS
if [[ ! -e $DIRETORIOKEY/key.fija ]]; then
if [[ $(cat $DIRETORIOKEY/used 2>/dev/null) = "" ]]; then
# at now + 1440 min <<< "rm -rf ${DIRETORIOKEY}*" # ¡PROGRAMADOR!
echo "$USRIP" > $DIRETORIOKEY/used
echo "$(date |cut -d' ' -f3,4)" > $DIRETORIOKEY/used.date
fi #COMPROBAR SI LA IP ES VARIABLE
#COMPRUEBA SI LA LLAVE FIJA ESTÁ EN LA IP CORRECTA
if [[ $(cat $DIRETORIOKEY/used) != "$USRIP" ]]; then
  # BLOQUEO DE INSTALACIÓN CON IP NO VÁLIDA
  log="/etc/gerar-sh-log"
  echo "USUARIO: $(cat $DIRETORIOKEY.name) IP FIJA: $(cat $DIRETORIOKEY/keyfixa) UTILIZÓ IP: $USRIP" >> $log
  echo "SU CLAVE FIJA HA SIDO BLOQUEADA" >> $log
  echo "-----------------------------------------------------" >> $log
  rm -rf ${DIRETORIOKEY}*
  exit #CLAVE NO VÁLIDA, FINALIZAR SOLICITUD
fi
fi
(
mkdir /var/www/$KEY
mkdir /var/www/html/$KEY
TIME="20+"
  for arqs in `cat $FILE`; do
  cp $DIRETORIOKEY/$arqs /var/www/html/$KEY/
  cp $DIRETORIOKEY/$arqs /var/www/$KEY/
  TIME+="1+"
  done
TIME=$(echo "${TIME}0"|bc)
sleep ${TIME}s
if [[ -d /var/www/$KEY ]]; then rm -rf /var/www/$KEY; fi
if [[ -d /var/www/html/$KEY ]]; then rm -rf /var/www/html/$KEY; fi
num=$(cat ${IVAR})
if [[ $num = "" ]]; then num=0; fi
let num++
echo $num > $IVAR
remover_key_usada
) & > /dev/null
}
[[ $1 = @(-[Ss]tart|-[Ss]|-[Ii]niciar) ]] && listen_fun && exit
[[ $1 = @(-[Ii]stall|-[Ii]|-[Ii]stalar) ]] && listen_fun && exit
server_fun
