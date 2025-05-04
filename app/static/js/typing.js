document.addEventListener("DOMContentLoaded", () => {
    const text = "Understanding emotions in news, shaping informed opinions.";
    const typingText = document.getElementById("typing-text");
    const cursor = document.getElementById("cursor");
    let charIndex = 0;
    const typingSpeed = 60;

    function type() {
        if (charIndex < text.length) {
            // 在光标前插入字符
            cursor.insertAdjacentText("beforebegin", text.charAt(charIndex));
            charIndex++;
            setTimeout(type, typingSpeed);
        }
    }

    setTimeout(type, 500);
});
