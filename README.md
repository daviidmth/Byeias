
![Logo](data/pictures/logo_new.png) 

The MVP is made of a backend and frontend which can be started through a Docker container. Since you don't have the time to run the MVP, the following will give you a quick overview of it.

## Frontend

The following pictures show what the frontend of the MVP looks like and show all the functions.

1. This is the general overview of the frontend. There is a field where you can paste in the text you want to review for any bias. In the picture, there is already an inserted text shown.

    ![Diagramm](data/pictures/start_frontend.jpeg)

2. If you click process, the backend, which is also explained in the next chapter, will check for biases.

    ![Diagramm](data/pictures/Result_frontend.jpeg)

3. Now you can hover over the detected biases and you get an explanation of what kind of bias it is and why it is a bias.

    ![Diagramm](data/pictures/Hover%20function_frontend.jpeg)

## Backend

The following picture shows the pipeline which is implemented in the MVP. It is important to mention that the PDF extraction function is working in the backend, but the implementation in the frontend is not done yet. The pipeline includes 3 components:

![Diagramm](data/pictures/Pipeline.png)

1. **Text processing module:** Extracts text from the input PDF, or receives the direct input text.
2. **Bert classifier:** Detects bias and categorizes it between racism and sexism.
3. **Mistral LLM:** Explains the detected biases, why they are a bias, and what the problem is with them.