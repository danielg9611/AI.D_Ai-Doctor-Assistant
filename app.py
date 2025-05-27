import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timezone

pages = {
    "Home": "Home",
    "Paciente": "Paciente",
    "DoctorHub": "DoctorHub"
}
pagina = st.query_params.get("page", "Home")


st.sidebar.image("docs/img/Logo-clear.png", use_container_width=False)


st.sidebar.markdown("## Navegación")
for key, label in pages.items():
    if pagina == key:
        st.sidebar.markdown(f"  **[{label}](?page={key})**")
    else:
        st.sidebar.markdown(f"  [{label}](?page={key})")


if st.query_params.get("page"):
    pagina = st.query_params["page"]


###########################################################################################
#########################################  HOME   #########################################
###########################################################################################

if pagina == 'Home':
    col1, col2, col3 = st.columns([2,6,2])
    with col2:
        st.image("docs/img/Logo-clear.png", width=600)
        st.markdown("<h1 style='text-align: center;'>Bienvenido a AID</h1>", unsafe_allow_html=True)
    st.markdown("""
    ### Tu asistente inteligente para consultas médicas

    **AID** es una herramienta diseñada para ayudar a doctores y pacientes a recopilar, organizar y analizar información clínica de manera eficiente y empática.

    - 🤖 **Asistente de paciente:** Recopila síntomas y antecedentes de manera amigable y comprensible.
    - 🩺 **Resumen automático:** Resume la información relevante para el doctor en formato claro y profesional.
    - 🧑‍⚕️ **Diagnóstico sugerido:** El sistema sugiere posibles padecimientos, especialidad recomendada y nivel de urgencia.

    ---
    """)
    st.markdown(
        """
        <div style="text-align: center;">
            Para comenzar, presiona el siguiete boton.
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown('--------')

    btn_col1, btn_col2, btn_col3 = st.columns([4,2,4])
    with btn_col2:
        if st.button("Comenzar"):
            st.query_params["page"] = "Paciente"


#############################################################################################
#########################################  DOCTOR   #########################################
#############################################################################################


if pagina == "DoctorHub":
    st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>AID Tickets</h1>",unsafe_allow_html=True)



    try:
        response = requests.get("http://api:8000/api/tickets/open")
        if response.status_code == 200:
            tickets = response.json().get("tickets", [])
            # st.write("Tickets encontrados:", len(tickets))

            table = []
            for ticket in tickets:

                fecha_ticket = datetime.fromisoformat(ticket["fecha"]).replace(tzinfo=timezone.utc)
                ahora = datetime.now(timezone.utc)
                espera = ahora - fecha_ticket
                espera_str = str(espera).split('.')[0]

                
                urgencia = ticket.get("urgencia", "").lower()
                if urgencia == "poco urgente":
                    color = "green"
                elif urgencia == "urgente":
                    color = "orange"
                elif urgencia == "muy urgente":
                    color = "red"


                urgencia_html = f'<span style="color:{color}; font-weight:bold;">{urgencia.capitalize()}</span>'


                table.append({
                    "Síntomas": ticket.get("sintomas", ""),
                    "Padecimiento": ticket.get("padecimiento", ""),
                    "Prescripción": ticket.get("prescripcion", ""),
                    "Especialidad": ticket.get("especialidad", ""),
                    "Espera": espera_str,
                    "Urgencia": urgencia_html
                })


            df = pd.DataFrame(table)
            tabla_html = df.to_html(escape=False, index=False)
            st.markdown(
                f"""
                <div style="width: 100vw; min-width: 1600px; overflow-x: auto;">
                    {tabla_html}
                </div>
                """,
                unsafe_allow_html=True
            )


        else:
            st.error(f"Error al obtener tickets: {response.status_code}")
    except Exception as e:
        st.error(f"Error de conexión: {e}")




###############################################################################################
#########################################  PACIENTE   #########################################
###############################################################################################


if pagina == 'Paciente':

    #################################  AGENTE  #################################


    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.prompts import PromptTemplate, SystemMessagePromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
    from langchain.agents import load_tools, initialize_agent, AgentType, create_react_agent, AgentExecutor
    from langchain.memory import ConversationBufferMemory
    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

    import re
    import json
    import os
    from dotenv import load_dotenv

    load_dotenv('.env')
    API_KEY = os.getenv("GEMINI_API_KEY")

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=API_KEY, temperature=0)
    memory = ConversationBufferMemory(memory_key='chat_history')
    tools = load_tools(['pubmed'], llm=llm)
    agent = initialize_agent(tools, llm, agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, memory=memory, verbose=True)

    nombre_paciente = "Daniel"

    system_message_text = f"""
    Tu nombre es AID (debes usar tu nombre en negritas), eres un asistente de un Doctor, especializado en recopilar toda la informacion sobre un paciente que el doctor pueda utilizar despues.
    Tu tarea principal es definir que sintomas tiene el paciente:{nombre_paciente} para que el doctor pueda hacer un diagnoistico acertado.
    Para esto haz de tener en cuenta que estas hablando con una persona que ademas de estar enferma y sentirse mal, no tiene grandes conocimientos
    sobre medicina. Tendras que ser empatico y comprensivo, buscando completar tu tarea de conocer los sintomas y el estado del paciente en el menor tiempo posible (no debras pasarte de 6 o 7 preguntas, debes escojer bien que preguntar).
    Cuando creas que tienes toda la informacion necesaria daras una ultima respuestas que sera y SOLO SERA la siguente:
            "Creo que tengo todo lo que necesito, para seguir con la consulta presione el boton de 'Abrir Consulta'. Gracias".
    Una vez hayas escrito el mensaje anterior, no puedes responder mas nada, si te preguntan sigue SOLO REPITIENDO EL ULTIMO MENSAJE
    """

    if not getattr(memory, "chat_memory", None) or not memory.chat_memory.messages:
        memory.chat_memory.add_message(SystemMessage(system_message_text))




    #################################  CHAT  #################################

    st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>AID Chat</h1>",unsafe_allow_html=True)




    if 'messages' not in st.session_state:
        st.session_state.messages = []
        st.session_state.memories = []


        result = agent.invoke("hola")['output']
        st.session_state.messages.append(AIMessage(result))
        st.session_state.memories.append(f'AI: {result}')
        memory.chat_memory.add_ai_message(result)



    for message in st.session_state.messages:
        if isinstance(message, HumanMessage):
            with st.chat_message('user'):
                st.markdown(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message('ai'):
                st.markdown(message.content) 


    prompt = st.chat_input('Say Something')

    if prompt:
        with st.chat_message('user'):
            st.markdown(prompt)
            st.session_state.messages.append(HumanMessage(prompt))
            st.session_state.memories.append(f'Human: {prompt}')
            memory.chat_memory.add_user_message(prompt)



        for message in st.session_state.messages[:-1]:  # Exclude the current prompt
            if isinstance(message, HumanMessage):
                memory.chat_memory.add_user_message(message.content)
            elif isinstance(message, AIMessage):
                memory.chat_memory.add_ai_message(message.content)


        result = agent.invoke(prompt)['output']

        with st.chat_message('ai'):
            st.markdown(result)
            st.session_state.messages.append(AIMessage(result))
            st.session_state.memories.append(f'AI: {result}')
            memory.chat_memory.add_ai_message(result)

        # sumary_memory.save_context({"input": prompt}, {"output": result})


    #################################  TICKET  #################################




    st.markdown('-----')

    btn_col1, btn_col2, btn_col3 = st.columns([3,2,3])


    with btn_col2:
        disabled_btn = len(st.session_state.memories) < 2
        if st.button("Abrir Consulta", disabled=disabled_btn):

        #################################  RESUMEN  #################################

            chat_history = '\n'.join(st.session_state.memories)

            resumen_prompt = f"""
                Resume la siguiente conversación entre paciente y asistente en formato de bulletpoints claros y concisos, resaltando síntomas, antecedentes y cualquier información relevante para el doctor. No es necesario decir el nombre del paciente ni el motivo de la consulta, solo se necesitan observaciones medicas:

                Conversación:
                {chat_history}

                Resumen en bulletpoints:
                """


            resumen = llm.invoke(resumen_prompt).content



            sintomas_prompt = f"""
                A partir del siguiente texto, extrae únicamente los síntomas mencionados por el paciente. 
                Ignora antecedentes, diagnósticos, prescripciones y cualquier otra información. 
                Devuelve solo la lista de síntomas, separados por comas, sin ningún texto adicional antes o después.
                Si hay solo un sintoma, devuelve solo ese
                Texto:
                {resumen}
                """


            sintomas = llm.invoke(sintomas_prompt).content
            


        #################################  DOCTOR  #################################


            doctor_prompt = f"""
                Eres un doctor de especializacion general, tu tarea es definir que padecimiento tiene un paciente basandote en un resumen de sintomas:

                Resumen:
                {resumen}

                Debes definir tres cosas:
                1. Padecimiento: Que enfermedad es la mas posible que tenga el paciente segun los sintomas dados. En caso de existir ambiguiedad, puedes hacer una lista con un maximo de 3. PERO TU OBJETIVO ES SACAR SOLO 1, EL DE MAS PROBABILIDAD
                2. Especialiad: Que especialidad de la medicina es la mas indicada para tratar estos sintomas o padecimientos. ej. (General, Dermatologo, etc...).
                3. Urgencia: Debes definir si el paciente debe tratarse de manera: "poco urgente", "urgente" o "muy urgente".


                La respuesta se usara para meter los datos en una base de datos asi que debe ser ÚNICAMENTE el siguiente objeto JSON, sin ningún texto antes o después, ni explicaciones, ni comentarios. NO uses markdown, ni comillas triples, ni ningún texto antes o después. SOLO el objeto JSON.:
                {{
                "padecimiento": "...",
                "especialidad": "...",
                "urgencia": "..."
                }}

                NO uses markdown, ni comillas triples, ni ningún texto antes o después. SOLO el objeto JSON.
                
                """

            doctor = initialize_agent(tools, llm, agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,memory=memory, verbose=True, handle_parsing_errors=True)

            data = doctor.invoke(doctor_prompt)['output']

            json_match = re.search(r'\{.*\}', data, re.DOTALL)
            if json_match:
                data = json_match.group(0)

            data = json.loads(data)
            data['prescripcion'] = 'Reservada'
            data['sintomas'] = sintomas
            data['paciente'] = 1
            data['doctor'] = 1


            try:
                response = requests.post(
                    "http://api:8000/api/tickets/post",
                    json=data
                )
                if response.status_code == 200:
                    st.markdown("### Enviado")
                else:
                    st.error(f"Error al crear ticket: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Error de conexión al crear ticket: {e}")
