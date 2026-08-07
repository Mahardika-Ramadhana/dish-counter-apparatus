import wifi_manager
from unittest.mock import patch, MagicMock

with patch('subprocess.run', side_effect=Exception("command failed")), \
     patch('wifi_manager.socket.socket') as mock_socket:
    
    mock_sock_instance = MagicMock()
    mock_sock_instance.getsockname.return_value = ("10.0.0.5", 12345)
    mock_socket.return_value = mock_sock_instance
    
    ip = wifi_manager.get_current_ip()
    print("IP returned:", ip)

