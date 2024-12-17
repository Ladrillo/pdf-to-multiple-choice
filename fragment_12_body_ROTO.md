#### 1.7. Bases de datos centralizadas
###### y distribuidas  
Una base de datos centralizada es una base de datos que
está almacenada de manera íntegra en un solo lugar, es
decir, en una misma máquina. Sin embargo y tal y como
se comentaba en el apartado anterior, una base de datos
**distribuida (BDD) es un conjunto de BBDD que se en-**
cuentran lógicamente relacionadas. Esto significa que se
distribuyen en diferentes sitios, de forma que se necesita
una interconexión de red para comunicarse. A continuación, detallamos con más precisión cada una de ellas:  
**Base de datos centralizada (BDC)**  
|Definición|Las BBDD centralizadas son aquellas que se encuentran almacenadas en una única computadora, por lo que el sistema informático no interacciona con ninguna otra máquina. Ejemplos de estos sistemas pueden ser BBDD básicas de un solo usuario o BBDD de alto rendimiento, implantadas en grandes sistemas.|
|---|---|
|Características|Almacena todos los componentes en una única máquina. No tiene demasiados elementos de procesamiento. Componentes: datos, software de gestión de BBDD y dispositivos de almacenamiento.|
|Ventajas|No presenta redundancia ni inconsistencia, ya que se focaliza todo en un sistema central. Si se tratara de una BD no centra- lizada, existiría redundancia de la información y, por tanto, problemas con el espacio de almacenamiento. Puede aplicar restricciones de seguridad. Rendimiento óptimo al procesar datos. Se evita la inconsistencia de los datos, ya que solo existe una sola entrada para cada dato almacenado.|
|Inconvenientes|Ante un problema, la recuperación de datos es complicada. No existe la posibilidad de repartir las tareas al intervenir sola- mente una máquina. Si un sistema falla, perdemos la disponibilidad de la información. Los mainframes (ordenadores centrales) ofrecen una relación entre el precio y el rendimiento bastante costosos.|  
usuario o BBDD de alto rendimiento, implantadas en grandes
sistemas.  
Componentes: datos, software de gestión de BBDD y dispositivos
de almacenamiento.  
-----  
|Col1|Base de datos distribuida (BDD)|
|---|---|
|Definición|Una BDD es aquella en la que interviene un conjunto de múltiples BDD relacionadas. Se encuentra en diferentes espacios lógicos y geográficos, pero está interconectada por una red. Estas BBDD son capaces de procesar de una forma autónoma, es decir, pueden trabajar de forma local o distribuida.|
|Características|Autonomía: los componentes, el SO y la red son independientes y cada uno realiza las diferentes operaciones desde su propio sitio. No necesita ni depende de una red central para obtener un servicio. Presenta la posibilidad de leer y escribir datos ubicados en lugares diferentes de la red. Puede convertir transacciones de usuarios en instrucciones para manipular datos.|
|Ventajas|Acceso rápido. Al intervenir varios nodos el procesamiento es más rápido. Los nuevos nodos que intervengan se crean de forma rápida y fácil. Mejora la comunicación entre distintos nodos. Refleja una estructura organizativa donde las BBDD se almacenan en los departamentos donde tienen relación. Bajo coste a la hora de crear una red de pequeñas computadoras. Al presentar una red de BBDD se implementa de forma modular. Esto hace que las operaciones de modificar, insertar o eliminar alguna BD sean mucho más fáciles que en el ejemplo anterior.|
|Inconvenientes|Presenta una estructura de diseño más compleja. Aumenta el riesgo de violaciones de seguridad. Mecanismos de recuperación más complejos, debido a que existen muchos más datos.|  
Los nuevos nodos que intervengan se crean de forma rápida y fácil.  
Mejora la comunicación entre distintos nodos.  
Bajo coste a la hora de crear una red de pequeñas computadoras.  
Al presentar una red de BBDD se implementa de forma modular.  
**Componentes: hardware y software**  
Refleja una estructura organizativa donde las BBDD se almacenan
en los departamentos donde tienen relación.  
A nivel de componentes hardware, las bases de datos Distribuidas suponen un mayor uso de infraestructura, ya que,
a diferencia de las bases de datos Centralizadas, las primeras ubican sus datos en más de una máquina (denominados
nodos o sitios).  
En referencia al software necesario, las bases de datos Distribuidas deben interconectar los nodos que las componen,
por lo que necesitan de una red a través de la cual transmitir la información entre los mismos.  
Esto hace que las operaciones de modificar, insertar o eliminar  
-----  
**Niveles de procesamiento de consultas: procesadores**
**locales y distribuidos**  
En los procesadores locales solamente se hace referencia
tanto a tablas como a datos locales, es decir, a aquellos que
pertenecen a una misma instancia en una única máquina.
Las subconsultas que se ejecutan en un nodo (consulta
local) se van a optimizar utilizando el esquema local del
nodo. Los diferentes algoritmos se pueden elegir para
ejecutar las operaciones relacionales.  
En los procesadores distribuidos, en cambio, el objetivo
principal va a ser pasar las transacciones de usuario a
instrucciones para poder manipular los datos. El principal
problema que presentan es de optimización, ya que se
determina el orden en el que se realizan el número mínimo
de operaciones.  
**CONCEPTO**  
El procesamiento de consultas es bastante
más complicado en los procesadores distribuidos que en los locales. Esto se debe a que en
los distribuidos interviene un gran número de
parámetros que pueden afectar al rendimiento
de las consultas que se tengan que realizar.  
La función más importante de un procesador de consultas
relacionales va a ser transformar una consulta de una especificación de nivel alto (normalmente en cálculo relacional)
en otra equivalente de bajo nivel (normalmente en álgebra
relacional).  
Esta trasformación se debe llevar a cabo y, si se consigue,
debe ser perfectamente correcta y eficiente.  
buidos que en los locales. Esto se debe a que en
los distribuidos interviene un gran número de
parámetros que pueden afectar al rendimiento  
relacionales va a ser transformar una consulta de una especificación de nivel alto (normalmente en cálculo relacional)  
**Bloqueo y concurrencia. Transacciones distribuidas**  
de las consultas que se tengan que realizar.  
La función más importante de un procesador de consultas  
Cuando nos referimos a los SGBD debemos señalar que
estamos ante sistemas concurrentes. Estos sistemas van
a ejecutar sus consultas y estas se van a ir procesando al
mismo tiempo.  
Las transacciones distribuidas se pueden definir como
transacciones planas o anidadas, que pueden acceder a
objetos que han sido administrados por diferentes servidores. Cuando una transacción distribuida finaliza, esta
necesita que todos los servidores que han formado parte
del proceso verifiquen su buen funcionamiento. En caso de
que no se pueda verificar, debe abortar la transacción. Este
mecanismo se puede llevar a cabo gracias a su propiedad
de atomicidad.  
en otra equivalente de bajo nivel (normalmente en álgebra  
-----  
**Distribución de los datos**  
La distribución de los datos es una tarea que corresponde
al diseñador. Este se va a encargar de elegir dónde se va a
posicionar y qué esquema va a representar dicha BD. Podemos encontrar las siguientes distribuciones: centralizadas,
replicadas, particionadas e híbridas.  
**• Centralizada: esta distribución es muy parecida al mo-**
delo cliente/servidor, en el que la base de datos está
centralizada en un nodo central y se distribuye entre los
distintos clientes. La desventaja que supone utilizar esta
distribución es que la disponibilidad depende de un solo
nodo.  
**• Replicadas: es un esquema muy costoso, ya que cada**
nodo va a tener información duplicada. Es más lento,
porque tiene muchos datos a almacenar, pero merece la
pena a largo plazo, ya que va a tener mucha disponibilidad a la hora de leer la información.  
**• Particionadas: en este caso solo tenemos una copia de**
cada nodo. De todas formas, cada nodo alojará algunos
fragmentos de la BD. Esto hace que el coste sea más reducido aunque, también, va a tener menos disponibilidad
que el anterior.  
**• Híbridas: aquí vamos a representar la partición y replica-**
ción del sistema.  
fragmentos de la BD. Esto hace que el coste sea más reducido aunque, también, va a tener menos disponibilidad
que el anterior.  
**Seguridad y recuperación de la información en bases**
**de datos distribuidas**  
**• Híbridas: aquí vamos a representar la partición y replica-**
ción del sistema.  
Existen diferentes tipos de ataques a la seguridad entre los
que podemos destacar: de privacidad y confidencialidad
de los datos, los que están asociados a la autenticación y
los que deniegan al servicio.  
En cuanto a las herramientas de seguridad, debemos señalar los distintos protocolos de seguridad, el cifrado de las
claves y los cortafuegos.  
Para poder recuperar los datos, debemos tener activa la
tolerancia a fallos que permite que, en caso de fallo de
algún componente, el sistema siga funcionando de forma
correcta.  
**Seguridad y recuperación de la información en bases**
**de datos distribuidas**  
**Arquitectura-implementaciones: múltiples y**
**federadas**  
Las BBDD federadas son un conjunto de sistemas de BBDD
que trabajan de forma cooperativa y autónoma.  
Los usuarios pueden acceder a los datos a través de una
interfaz. Esta interfaz no tiene diseñado un esquema total  
-----  
donde estén todos los datos, sino que contiene diferentes
esquemas más pequeños que hay que unificar.  
Las **BBDD federadas parecen BBDD normales, pero no**
tienen existencia física por sí solas: son una vista lógica.  
Las **BBDD múltiples actúan como una interfaz de varios**
componentes diferentes. Una BD múltiple cuenta con distintas operaciones que facilitan el acceso a la información,
manteniendo la consistencia de esta y ofreciendo un acceso uniforme a los servicios.  
_Arquitectura_  
**Diseño y gestión de BBDD distribuidas**  
Cuando necesitemos diseñar una BD distribuida, tendremos que dar una serie de pasos que nos permitan tener el
diseño correcto para almacenar nuestros datos. Existen una
serie de pasos que debemos seguir a la hora de diseñar una
BD distribuida, veamos los más importantes:  
-----  
**1. Diseñar el esquema conceptual: para empezar, nece-**
sitaremos detallar el esquema conceptual de toda la BD.  
**2. Diseñar la BD: posteriormente, organizar el esquema**
conceptual y establecer sus métodos de acceso.  
**3. Diseñar fragmentación: necesitaremos fragmentar,**
es decir, realizar subdivisiones en fragmentos de las
diferentes partes de la BD.  
**4. Diseñar asignación de fragmentos: por último, or-**
ganizar y seleccionar cómo se van a unir los diferentes
fragmentos previamente creados.  
Para después gestionar correctamente nuestra BD, necesitaremos tener una BD estable, cuyas relaciones sean
coherentes y su interconexión entre los nodos sea correcta.
Para administrar las transacciones en BBDD distribuidas
podemos utilizar lo que se conoce como Administrador de
**Transacciones Distribuidas (DTM). Esto es un programa**
que procesa y coordina las consultas o transacciones de
nuestra BD.  
-----  
###### ponte a prueba  
**Indica cuál de las siguientes opciones es**
**una ventaja de trabajar con bases de datos**
**distribuidas.**  
a) Supone un bajo coste a la hora de crear una
red de computadoras pequeña.  
b) Aumenta el nivel de seguridad.  
c) Los mecanismos de recuperación de datos
son óptimos gracias a que intervienen
distintos nodos.  
d) Solamente tiene una entrada para cada dato
que se almacena.  
**Indica cuál de las siguientes opciones perte-**
**nece a una base de datos centralizada.**  
a) No depende ni necesita una red central para
obtener servicio.  
b) No tiene demasiados elementos de procesa-
miento.  
c) No almacena todos los componentes en una
única máquina.  
d) No puede aplicar restricciones de seguridad.  
**El diseñador es el encargado de distribuir**
**los datos en una base de datos. ¿Cuál de las**
**siguientes opciones se corresponde con un**
**esquema costoso, en el que cada uno de los**
**nodos tendrá la información duplicada, que**
**también dispone de mucha disponibilidad pero**
**que resulta más lento al tener muchos datos?**  
a) Distribución centralizada.  
b) Distribución replicada.  
c) Distribución particionada.  
d) Distribución híbrida.  
**Indica cuál de las siguientes opciones es una**
**de las ventajas principales de las bases de**
**datos centralizadas.**  
a) Ante un problema, la recuperación de datos
es complicada.  
b) Si un sistema falla, perdemos la disponibi-
lidad de la información.  
c) Rendimiento óptimo al procesar datos.  
d) Acceso rápido.  
c) No almacena todos los componentes en una  
**los datos en una base de datos. ¿Cuál de las**  
-----