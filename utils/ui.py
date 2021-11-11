import streamlit as st


def striken(text):
    return "".join(chr(822) + t for t in text)


def to_do(st_commands, checkbox_id):
    cols = st.columns((1, 20))
    done = cols[0].checkbox(" ", key=checkbox_id)
    if done:
        _, title, *_ = st_commands[0][1].split("**")
        cols[1].write(f"<s> **{title}** </s>", unsafe_allow_html=True)
    else:
        for (cmd, *args) in st_commands:
            with cols[1]:
                if cmd == st.write:
                    st.write(*args, unsafe_allow_html=True)
                else:

                    cmd(*args)
    st.write("")
    return done


def load_keyboard_class():
    st.write(
        """<style>
        .kbdx {
        background-color: #eee;
        border-radius: 3px;
        border: 1px solid #b4b4b4;
        box-shadow: 0 1px 1px rgba(0, 0, 0, .2), 0 2px 0 0 rgba(255, 255, 255, .7) inset;
        color: #333;
        display: inline-block;
        font-size: .85em;
        font-weight: 700;
        line-height: 1;
        padding: 2px 4px;
        white-space: nowrap;
    }
    </style>""",
        unsafe_allow_html=True,
    )


def to_button(text):
    return f'<span class="kbdx">{text}</span>'
