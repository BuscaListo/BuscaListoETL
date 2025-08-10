from webscraping.extractors.extractor_daka import DakaExtractor


class ConfigFactory:
    
    extractors = {
        'daka': DakaExtractor,
    }