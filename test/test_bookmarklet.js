/*
You are a helpful assistant that answers questions using Tcl code.
You can execute Tcl code on behalf of the user by wrapping it in a tcl code block with the first line as "### tcl".
You can prompt the user to click the Run Tcl Code button to execute the code.
If the user does click the button, the API will return one or more of the following:
- output: output produced by the code block (if any), which may include error messages
- result: the result of the last command in the code block (if non-empty)
- silent completion: if the code produced no output and no result
In general, you should prefer returning a result over using puts to produce output.
If the user asks for something else, you will provide a regular response.
*/

/*
api_response:
1 2 3 4 5 6 7 8 9 10
*/

function sendQuery (query) {
    textarea = document.forms[1].querySelector("textarea");
    textarea.focus();
    textarea.setRangeText(query, textarea.selectionStart, textarea.selectionEnd, "end");
    textarea.dispatchEvent(new Event('input', { bubbles: true }));

    button = document.querySelector('button[type="submit"]')
    button.click()
}
/*
async function waitClipboard(prefix = "api_response:", timeoutMs = 60000, intervalMs = 1000) {
    const start = Date.now();
    console.log("Waiting for clipboard match with prefix:", prefix, start);
    
    while (Date.now() - start < timeoutMs) {
        try {
            const text = await navigator.clipboard.readText();
            if (text.startsWith(prefix)) {
                console.log("Detected clipboard match:", text);
                return text;
            }
        } catch (err) {
            console.warn("Clipboard read failed:", err);
        }
        await new Promise(resolve => setTimeout(resolve, intervalMs));
    }
    
    throw new Error("Timed out waiting for clipboard match");
}
*/

let polling = false;

async function startClipboardPolling() {
    if (polling) return;
    polling = true;
    
    console.log("Starting clipboard polling...");
    
    while (true) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        if (!document.hasFocus()) continue;
        
        try {
            const text = await navigator.clipboard.readText();
            
            if (text.startsWith("api_response:")) {
                console.log("API response:", text);
                await sendQuery(text);
                
                // Clear clipboard to prevent repeat handling
                await navigator.clipboard.writeText("");
                console.log("Clipboard cleared.");
            }
        } catch (err) {
            if (err.name !== "NotAllowedError") {
                console.error("Unexpected clipboard error:", err);
            }
            // Otherwise silently skip
        }
    }
}


function handleCopyButton(oldButton) {
    language = oldButton.parentElement.parentElement.querySelector('div').querySelector('p').textContent;
    console.log("handleCopyButton(oldButton) language:", language);

    if (language == "tcl") {
        console.log("language is tcl");
        if (oldButton.dataset.listenerAttached == "true") return; // Prevent double-binding
        console.log("attaching listener to button");
        oldButton.dataset.listenerAttached = "true";
        oldButton.textContent = "🏃 Run Code";  // ▶

        const newButton = oldButton.cloneNode(true);
        oldButton.parentElement.replaceChild(newButton, oldButton);

        newButton.addEventListener('click', async (event) => {
            const clickedButton = event.currentTarget;
            content = clickedButton.parentElement.parentElement.nextElementSibling.textContent;
            const prefixedContent = `### tcl\n${content}`;

            try {
                await navigator.clipboard.writeText(prefixedContent);
                console.log('Copied to clipboard:', prefixedContent);
            } catch (err) {
                console.error('Clipboard write failed:', err);
            }

            /*
            console.log("Waiting for clipboard match");
            const query = await waitClipboard("api_response:");
            sendQuery(query);
            */
            
            startClipboardPolling();
            
        });
    }
}

function test_handleCopyButton() {
    // Change copy button to run code
    buttons = document.querySelectorAll('button[aria-label="Copy Code"]');
    copybtn = buttons.item(buttons.length - 1);

    handleCopyButton(copybtn);
}

function addRunButtons() {
    const buttons = document.querySelectorAll?.('button[aria-label="Copy Code"]') ?? [];
    buttons.forEach(handleCopyButton);
}

if(window.copyButtonObserver) {
    window.copyButtonObserver.disconnect();
}

const observer = new MutationObserver(mutations => {
    for (const mutation of mutations) {
        for (const node of mutation.addedNodes) {
            if (!(node instanceof HTMLElement)) continue;
            if (
                node.tagName === 'P' ||
                (node.tagName === 'SPAN' && node.getAttribute('data-state') === 'tooltip-hidden')
            ) {
                console.log(node);
                
                // Look for any new "Copy Code" buttons and chage them to runners
                addRunButtons();
            }
        }
    }
});

// Start observing the document body for new elements being added
observer.observe(document.body, {
    childList: true,
    subtree: true
});

window.copyButtonObserver = observer;
addRunButtons();

// Bookmarklet snippet (insert your real key here)
javascript:(() => { let e=!1;function t(t){if(language=t.parentElement.parentElement.querySelector("div").querySelector("p").textContent,console.log("handleCopyButton(oldButton) language:",language),"tcl"==language){if(console.log("language is tcl"),"true"==t.dataset.listenerAttached)return;console.log("attaching listener to button"),t.dataset.listenerAttached="true",t.textContent="🏃 Run Code";const o=t.cloneNode(!0);t.parentElement.replaceChild(o,t),o.addEventListener("click",(async t=>{const o=t.currentTarget;content=o.parentElement.parentElement.nextElementSibling.textContent;const n=`### tcl\n${content}`;try{await navigator.clipboard.writeText(n),console.log("Copied to clipboard:",n)}catch(e){console.error("Clipboard write failed:",e)}!async function(){var t;if(!e)for(e=!0,console.log("Starting clipboard polling...");;)if(await new Promise((e=>setTimeout(e,1e3))),document.hasFocus())try{const e=await navigator.clipboard.readText();if(e.startsWith("api_response:")){console.log("Detected API response in clipboard:",e),await(t=e,textarea=document.forms[1].querySelector("textarea"),textarea.focus(),textarea.setRangeText(t,textarea.selectionStart,textarea.selectionEnd,"end"),textarea.dispatchEvent(new Event("input",{bubbles:!0})),button=document.querySelector('button[type="submit"]'),void button.click());try{await navigator.clipboard.writeText(""),console.log("Clipboard cleared.")}catch(e){console.warn("Failed to clear clipboard:",e)}}}catch(e){"NotAllowedError"!==e.name&&console.error("Unexpected clipboard read error:",e)}}()}))}}function o(){(document.querySelectorAll?.('button[aria-label="Copy Code"]')??[]).forEach(t)}window.copyButtonObserver&&window.copyButtonObserver.disconnect();const n=new MutationObserver((e=>{for(const t of e)for(const e of t.addedNodes)e instanceof HTMLElement&&("P"===e.tagName||"SPAN"===e.tagName&&"tooltip-hidden"===e.getAttribute("data-state"))&&(console.log(e),o())}));n.observe(document.body,{childList:!0,subtree:!0}),window.copyButtonObserver=n,o(); })();
