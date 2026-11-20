from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM

load_dotenv()

llm = LLM(model="gemini/gemini-3.5-flash-lite")

agente = Agent(
    role="Asistente de DevOps",
    goal="Explicar conceptos de DevOps de forma simple",
    backstory="Eres un ingeniero DevOps que enseña a estudiantes.",
    llm=llm,
)

tarea = Task(
    description="Explica en 3 frases qué es un contenedor Docker.",
    expected_output="Un texto de máximo 3 frases en español.",
    agent=agente,
)

equipo = Crew(agents=[agente], tasks=[tarea])
resultado = equipo.kickoff()
print(resultado)