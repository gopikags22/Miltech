// Start Webcam for target detection or semaphore/morse
function startWebcam() {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(function(stream) {
        var videoElement = document.querySelector('video');
        videoElement.srcObject = stream;
      })
      .catch(function(err) {
        console.log("Error accessing webcam: " + err);
      });
  }
  
  // Real-time voice translation function with multiple language support
  function startVoiceTranslation() {
    console.log("Voice translation started...");
  
    // Set up the Speech Recognition API
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US'; // Default language (English)
    recognition.interimResults = false; // Disable interim results
    recognition.maxAlternatives = 1; // Max alternative translations
  
    // Start listening to speech
    recognition.start();
  
    // When speech is recognized
    recognition.onresult = function(event) {
      const spokenText = event.results[0][0].transcript;
      console.log("Recognized speech:", spokenText);
  
      // Call the translation API
      translateText(spokenText);
    };
  
    // When there's an error in speech recognition
    recognition.onerror = function(event) {
      console.error('Speech recognition error:', event.error);
    };
  
    // Optional: Add language change functionality
    document.getElementById('language-selector').addEventListener('change', function(e) {
      recognition.lang = e.target.value;
    });
  }
  
  // Translate text using Google Translate API (or similar translation API)
  function translateText(text) {
    const targetLanguage = document.getElementById('language-selector').value || 'en'; // Default to English if no selection
  
    // API URL for Google Translate or another translation API
    const apiUrl = `https://translation.googleapis.com/language/translate/v2?key=YOUR_API_KEY`;
  
    // Make an API call to translate the text
    fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        q: text,
        target: targetLanguage
      })
    })
      .then(response => response.json())
      .then(data => {
        const translatedText = data.data.translations[0].translatedText;
        document.getElementById("translation-output").innerText = `Translated Text: ${translatedText}`;
      })
      .catch(error => {
        console.error('Error translating text:', error);
      });
  }
  
  // Typing animation function
  window.onload = function() {
    const typedTextElement = document.querySelector('.typed-text');
    const text = 'MilTech OpsSim';
    
    let index = 0;
    const typingSpeed = 100; // Adjust typing speed
  
    function typeText() {
      if (index < text.length) {
        typedTextElement.innerHTML += text.charAt(index);
        index++;
        setTimeout(typeText, typingSpeed);
      }
    }
  
    typeText();
  };