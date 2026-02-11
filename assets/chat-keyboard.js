/**
 * Chat keyboard shortcut: Shift+Enter to send message.
 *
 * Dash automatically loads all JS files under assets/.
 * Enter alone keeps the default textarea behavior (newline).
 */
document.addEventListener("DOMContentLoaded", function () {
    document.addEventListener("keydown", function (e) {
        if (e.target.id !== "chat-input") return;
        if (e.key === "Enter" && e.shiftKey) {
            e.preventDefault();
            var sendBtn = document.getElementById("chat-send-button");
            if (sendBtn) {
                sendBtn.click();
            }
        }
    });
});
