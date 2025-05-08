import os
from uuid import uuid4
from botly import Botly
from core.logging import logger
from streamlit import (
    logo,
    title,
    write,
    status,
    spinner,
    success,
    markdown,
    chat_input,
    chat_message,
    file_uploader,
    session_state,
    set_page_config,
)


class BotlyUI:
    def __init__(self):
        """
        Initialize the BotlyUI class.

        This method sets the page title, title icon, and logo, and then
        initializes the session state and calls the ui method to render the
        interface.

        Attributes:
            page_title (str): The title of the page.
            page_title_icon (str): The icon to display in the title bar.
            page_logo (streamlit.components.logo): The logo to display in the
                sidebar.
            session (streamlit.session_state): The session state.
        """

        self.page_title = "Botly"
        self.page_title_icon = "\U0001f916"
        self.creator = "   by Sumit Kumar  👨‍💻"
        self.page_logo = logo(
            image=str(
                os.path.join(
                    os.getcwd(),
                    "resources/botly_icon.png",
                )
            ),
            size="large",
            icon_image=str(
                os.path.join(
                    os.getcwd(),
                    "resources/botly_icon.png",
                )
            ),
        )
        self.session = session_state
        self.ui()

    def create_session_state(self):
        """
        Create the session state.

        This method initializes the session state if it does not already exist.
        It sets the session id to a random UUID, and initializes the messages
        list, document, document path, document saved, document uploaded,
        document ingested, and botly attributes.

        Returns:
            None
        """
        if not self.session:
            logger.info("Initializing session state...")
            self.session.id = uuid4().hex
            self.session.messages = []
            self.session.document = None
            self.session.document_path = None
            self.session.document_saved = False
            self.session.document_uploaded = False
            self.session.document_ingested = False
            self.session.botly = Botly()
            logger.info("Session state initialized.")

    def save_document(self):
        """
        Save the uploaded document to disk.

        This method saves the uploaded document to disk and sets the
        document_saved session state to True.

        Returns:
            None
        """
        if self.session.document_uploaded and not self.session.document_saved:
            logger.info("Saving document...")
            file_path = os.path.join(
                os.getcwd(),
                f"{self.session.id}.pdf",
            )
            with open(file_path, "wb") as f:
                f.write(self.session.document.getvalue())
                self.session.document_path = file_path

            ##
            if self.session.document_path:
                self.session.document_saved = True

    def upload_document(self):
        """
        Upload a document to use for RAG.

        This method displays a file uploader widget and saves the uploaded
        document to the session state. If a document is uploaded, it sets the
        document_uploaded session state to True.

        Returns:
            None
        """
        if not self.session.document_uploaded:
            write(
                "\n\n📌 Note: To receive a response based on the attached document, please mention @pdf in your message."
            )
            self.session.document = file_uploader(
                label="RAG Document",
                type="pdf",
                accept_multiple_files=False,
                key="rag_document",
                disabled=False,
            )

            ##
            if self.session.document:
                self.session.document_uploaded = True

    def ingest_document(self):
        """
        Ingest the uploaded document.

        This method processes the uploaded document and creates a vector store
        for it. It checks if the document has been saved and uploaded but not
        yet ingested. If so, it uses the `document_consumer` method to process
        the document and the `vector_store_generator` to generate the vector
        store. It then marks the document as ingested and indicates that the
        document is available for retrieval-augmented generation (RAG).

        Returns:
            None
        """

        if (
            self.session.document_saved
            and self.session.document_uploaded
            and not self.session.document_ingested
        ):
            logger.info("Ingesting document...")
            with spinner(
                text="In progress",
                show_time=True,
            ):
                self.session.botly.document_consumer(self.session.document_path)
                self.session.botly.vector_store_generator()
                self.session.botly.have_document = True
                self.session.document_ingested = True
                success("Vector store generated.")
                logger.info("Document ingested.")

    def add_bot_details(self):
        """
        Add details about the bot to the interface.

        This method adds the title of the page, and if a document has been saved,
        uploaded, and ingested, it displays a note and the name of the document.

        Attributes:
            page_title (str): The title of the page.
            page_title_icon (str): The icon to display in the title bar.
            session (streamlit.session_state): The session state.
        """
        # title(self.page_title_icon + self.page_title)  # + self.creator,
        set_page_config(page_title=self.page_title)
        markdown(
            """

            <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600&display=swap');

            .orbitron-title {
                font-family: 'Orbitron', sans-serif;
                font-size: 36px;
                color: #00bfff;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            </style>

            <div class="orbitron-title">
                Botly
            </div>
        """,
            unsafe_allow_html=True,
        )

        if (
            self.session.document_saved
            and self.session.document_uploaded
            and self.session.document_ingested
        ):
            write(
                "\n\n📌 Note: To receive a response based on the attached document, please mention @pdf in your message."
            )
            markdown(f":material/picture_as_pdf:  {self.session.document.name}")

    def render_message_history(self):
        """
        Display chat messages from history on app rerun.

        This method iterates over the `messages` attribute of the session state,
        which contains a list of dictionaries with the keys "role" and "content".
        For each message, it displays the content of the message within a
        `chat_message` container with the role of the message as the argument.

        Returns:
            None
        """
        for message in self.session.messages:
            with chat_message(message["role"]):
                markdown(message["content"])

    def user_interaction_console(self):
        """
        React to user input in the chat console.

        This method displays a `chat_input` widget with the label "Say something"
        and listens for user input. If the user enters a message, it displays the
        user message in a `chat_message` container with the role "user" and adds
        the user message to the chat history.

        If the user mentions "@pdf" in their message, it uses the `rag_chain` to
        generate a response based on the attached PDF document. Otherwise, it
        uses the `normal_chain` to generate a response.

        The response is displayed in a `chat_message` container with the role
        "assistant" and added to the chat history.

        Returns:
            None
        """
        prompt = chat_input("Say something")
        if prompt:
            logger.info("User message: %s", prompt)
            chat_message("user").markdown(prompt)
            self.session.messages.append(
                {
                    "role": "user",
                    "content": prompt,
                }
            )

            # response = self.session.botly.botly_reply(
            #     query=prompt,
            # )

            query = prompt.lower()
            response = ""

            logger.info("Generating response...")
            with status("Kindly wait! AI operations are in progress..."):
                if "@pdf" in query:
                    logger.info("Generating RAG response...")
                    if not self.session.botly.have_document:
                        write("Generating response...")
                        response = "Sorry, I cannot find any attached PDF to this conversation."
                    else:
                        write("Generating message context...")
                        self.session.botly.context_generator(
                            query=query,
                        )
                        write("Generating RAG response...")
                        response = self.session.botly.rag_chain.invoke(
                            {
                                "context": self.session.botly.formated_context_documents,
                                "question": query,
                            }
                        )
                else:
                    logger.info("Generating normal response...")
                    write("Generating response...")
                    response = self.session.botly.normal_chain.invoke(
                        {
                            "context": query,
                        }
                    )

            logger.info("Response generated: %s", response)
            with chat_message("assistant"):
                markdown(response)
            self.session.messages.append(
                {
                    "role": "assistant",
                    "content": response,
                }
            )

    def ui(self):
        """
        Render the UI of the chatbot.

        This method renders the UI of the chatbot by calling the following methods in sequence:
        1. create_session_state - Creates the session state and initializes the session state attributes.
        2. add_bot_details - Adds details about the bot to the interface.
        3. upload_document - Displays a file uploader to upload a PDF document to use for RAG.
        4. save_document - Saves the uploaded document to disk.
        5. ingest_document - Generates a vector store for the uploaded document.
        6. render_message_history - Displays chat messages from history on app rerun.
        7. user_interaction_console - Reacts to user input in the chat console, generating responses based on the user input.

        Returns:
            None
        """
        ##
        self.create_session_state()

        ##
        self.add_bot_details()

        ##
        self.upload_document()

        ##
        self.save_document()

        ##
        self.ingest_document()

        ##
        self.render_message_history()

        ##
        self.user_interaction_console()


if __name__ == "__main__":
    botly_ui = BotlyUI()
