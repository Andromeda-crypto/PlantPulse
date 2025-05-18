PlantPulse is a web app I built to help people keep their plants healthy by monitoring key environmental data like soil moisture, light, and temperature. It pulls this info from sensor data (right now simulated with CSV files) and shows it in interactive charts so you can really understand what’s going on with your plants over time. You can sign up, log in, and get a personalized dashboard that shows your plant’s recent data, and there’s a zoom feature where you pick a time range to dig into the details.

On the tech side, the backend is built with Python and Flask, which handles user sessions, data loading, and processing. For the charts and graphs, I use Plotly to make the data interactive and easy to explore. The frontend uses Bootstrap to keep everything responsive and clean across devices, with some custom CSS for styling. The app communicates between frontend and backend using JSON and fetch API calls, so it feels smooth and modern without page reloads. Eventually, I want to swap out the simulated data for real sensor inputs and add more personalized features, but for now, it’s a solid base for plant monitoring and data visualization.



