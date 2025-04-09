from rest_framework.decorators import api_view
from rest_framework.response import Response
from .pipeline import ask_question

@api_view(['POST'])
def ask(request):
    question = request.data.get('question', '')
    if not question:
        return Response({"error": "Question is required"}, status=400)
    answer = ask_question(question)
    return Response({"question": question, "answer": answer})