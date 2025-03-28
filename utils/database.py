from pymongo import MongoClient
from flask import current_app

class DatabaseManager:
    def __init__(self):
        self.client = MongoClient(current_app.config['MONGODB_URI'])
        self.db = self.client.crowd_analysis
        
    def store_analysis(self, analysis_results):
        self.db.analytics.insert_one({
            'timestamp': analysis_results['timestamp'],
            'count': analysis_results['count'],
            'density': analysis_results['density'],
            'movement': analysis_results['movement'],
            'anomalies': analysis_results['anomalies']
        })
    
    def get_historical_data(self, start_time=None, end_time=None):
        query = {}
        if start_time:
            query['timestamp'] = {'$gte': start_time}
        if end_time:
            query['timestamp'] = {'$lte': end_time}
            
        return list(self.db.analytics.find(query))