"""
Script para probar la creación de un bot en Recall.ai.

Uso:
  docker compose exec backend python /app/../scripts/test_recall_bot.py <MEETING_URL>

Ejemplo:
  docker compose exec backend python scripts/test_recall_bot.py "https://meet.google.com/abc-defg-hij"

Pasos:
  1. Crea una reunión en meet.new y quédate dentro
  2. Copia la URL de la reunión  
  3. Ejecuta este script con esa URL
  4. El bot debería unirse a la reunión en ~10-30 segundos
  5. Habla un poco para generar transcripción
  6. Termina la reunión
"""
import sys
import asyncio
import json

# Add app to path
sys.path.insert(0, '/app')

from app.services.recall_service import recall_service, RecallServiceError


async def main():
    if len(sys.argv) < 2:
        print("❌ Uso: python scripts/test_recall_bot.py <MEETING_URL>")
        print("   Ejemplo: python scripts/test_recall_bot.py 'https://meet.google.com/abc-defg-hij'")
        sys.exit(1)
    
    meeting_url = sys.argv[1]
    
    print(f"🔧 Configuración:")
    print(f"   Region: {recall_service.region}")
    print(f"   Base URL: {recall_service.base_url}")
    print(f"   API Key: {recall_service.api_key[:10]}...")
    print()
    
    # Test connection
    print("📡 Probando conexión...")
    connected = await recall_service.test_connection()
    if not connected:
        print("❌ No se puede conectar a Recall.ai")
        sys.exit(1)
    print("✅ Conexión OK")
    print()
    
    # Create bot
    print(f"🤖 Creando bot para: {meeting_url}")
    try:
        bot_data = await recall_service.create_bot(
            meeting_url=meeting_url,
            meeting_id=999,  # Test ID
            bot_name="MeetMind Test Bot"
        )
        
        bot_id = bot_data["id"]
        print(f"✅ Bot creado exitosamente!")
        print(f"   Bot ID: {bot_id}")
        print(f"   Status changes: {bot_data.get('status_changes', [])}")
        print()
        
        # Poll status for a bit
        print("⏳ Esperando que el bot se una a la reunión...")
        print("   (Ctrl+C para parar el polling)")
        print()
        
        for i in range(30):  # Poll for up to 60 seconds
            await asyncio.sleep(2)
            try:
                status_data = await recall_service.get_bot_status(bot_id)
                status_changes = status_data.get("status_changes", [])
                current = recall_service.get_current_status(status_changes)
                participants = status_data.get("meeting_participants", [])
                
                print(f"   [{i*2}s] Status: {current} | Participants: {len(participants)}")
                
                if current in ("in_call_recording", "in_call_not_recording"):
                    print(f"\n🎉 ¡Bot está en la reunión!")
                    print(f"   Participantes: {[p.get('name', '?') for p in participants]}")
                    break
                elif current in ("done", "error"):
                    print(f"\n⚠️  Bot terminó con status: {current}")
                    break
                    
            except Exception as e:
                print(f"   Error polling: {e}")
        
        print()
        print(f"📋 Resumen:")
        print(f"   Bot ID: {bot_id}")
        print(f"   Para ver status: GET {recall_service.base_url}/bot/{bot_id}")
        print(f"   Para eliminar: DELETE {recall_service.base_url}/bot/{bot_id}")
        
    except RecallServiceError as e:
        print(f"❌ Error creando bot: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹  Polling detenido. El bot sigue activo.")
        print(f"   Bot ID: {bot_id}")


if __name__ == "__main__":
    asyncio.run(main())
