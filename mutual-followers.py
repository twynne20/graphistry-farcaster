import requests
import pandas as pd
import graphistry

# Setup
api_key = "NEYNAR-API-KEY"  # Replace with your actual API key
curly_fid = 263428  
viewer_fid = 263428  

# Function to fetch followers with pagination (limit results for demonstration)
def fetch_followers(fid, viewer_fid, api_key, max_results=500):
    followers = []
    next_cursor = None
    while len(followers) < max_results:
        url = f"https://api.neynar.com/v1/farcaster/followers?fid={fid}&viewerFid={viewer_fid}&limit=150"
        if next_cursor:
            url += f"&cursor={next_cursor}"
        headers = {"accept": "application/json", "api_key": api_key}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            followers.extend(response_data['result']['users'])
            if 'next' in response_data['result'] and 'cursor' in response_data['result']['next']:
                next_cursor = response_data['result']['next']['cursor']
            else:
                break
        else:
            break
    return followers[:max_results]

# Fetch 'curly's followers (limited to 15 for demonstration)
curly_followers = fetch_followers(curly_fid, viewer_fid, api_key, max_results=500)

# Convert followers to a DataFrame
followers_df = pd.DataFrame(curly_followers)

# Create a dictionary to map user FIDs to their display names
fid_to_name = dict(zip(followers_df['fid'], followers_df['displayName']))

# Extract relevant columns for visualization
edges_data = []
for _, row in followers_df.iterrows():
    user_fid = row['fid']
    user_name = row['displayName']
    
    # Fetch the user's followers
    user_followers = fetch_followers(user_fid, viewer_fid, api_key, max_results=500)
    
    # Create edges between the user and their followers
    for follower in user_followers:
        follower_fid = follower['fid']
        if follower_fid in fid_to_name:
            follower_name = fid_to_name[follower_fid]
            edges_data.append({
                'source': user_name,
                'target': follower_name
            })

# print("Edges Data:")
# print(edges_data)

edges_df = pd.DataFrame(edges_data)
nodes_df = pd.DataFrame({
    'node': pd.concat([edges_df['source'], edges_df['target']]).unique()
})

# Add edges between 'curly' and all unique nodes
curly_edges = pd.DataFrame({
    'source': 'curly',
    'target': nodes_df['node'].unique()
})
edges_df = pd.concat([edges_df, curly_edges], ignore_index=True)

# print("Edges DataFrame:")
# print(edges_df)

# print("Nodes DataFrame:")
# print(nodes_df)

# Add 'curly' to the nodes DataFrame
nodes_df = pd.concat([nodes_df, pd.DataFrame({'node': ['curly']})], ignore_index=True)

# Initialize Graphistry
graphistry.register(api=3, username='graphistry-username', password='graphistry-password')

# Plot the graph
g = graphistry.edges(edges_df).bind(source='source', destination='target').nodes(nodes_df).bind(node='node')
g.plot(render=True)
