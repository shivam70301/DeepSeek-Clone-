import requests
from django.shortcuts import render
from django.conf import settings
from .models import ChatMessage


def chat_view(request):
    chat_history = []

    if request.method == 'POST':
        user_input = request.POST.get('message')

        try:
            payload = {
                "model": "deepseek/deepseek-r1-0528:free",  # or another model you want
                "messages": [
                    {"role": "user", "content": user_input}
                ]
            }

            headers = {
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": settings.OPENROUTER_SITE_URL,
                "X-Title": settings.OPENROUTER_SITE_TITLE,
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            bot_response = result['choices'][0]['message']['content']

        except Exception as e:
            bot_response = f"⚠️ Error: {str(e)}"

        ChatMessage.objects.create(user_message=user_input, bot_response=bot_response)
        chat_history = ChatMessage.objects.order_by('-timestamp')[:10][::-1]

    else:
        chat_history = ChatMessage.objects.order_by('-timestamp')[:10][::-1]

    return render(request, 'chat.html', {
        'chat_history': chat_history
    })
