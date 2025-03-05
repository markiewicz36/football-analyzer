import os
import json
import httpx
import logging
from dotenv import load_dotenv
from fastapi import HTTPException

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# API configuration
DEEPSEEK_API_BASE_URL = os.getenv("DEEPSEEK_API_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")


class DeepSeekClient:
    """
    Client for interacting with the DeepSeek API.
    """

    def __init__(self, api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_API_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(headers=self.headers, timeout=60.0)

    async def close(self):
        """Close the HTTP client session."""
        await self.client.aclose()

    async def _make_request(self, endpoint, method="POST", data=None):
        """
        Make a request to the DeepSeek API.

        Args:
            endpoint (str): API endpoint path
            method (str): HTTP method (POST, GET, etc.)
            data (dict, optional): Request payload

        Returns:
            dict: API response
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            if method == "POST":
                response = await self.client.post(url, json=data)
            elif method == "GET":
                response = await self.client.get(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            error_detail = str(e)
            if e.response.text:
                try:
                    error_json = e.response.json()
                    if "error" in error_json:
                        error_detail = error_json["error"]
                except:
                    error_detail = e.response.text
            raise HTTPException(status_code=e.response.status_code, detail=error_detail)
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    async def get_models(self):
        """Get available models."""
        return await self._make_request("v1/models", method="GET")

    async def analyze_match(self, home_team, away_team, match_data, league_data=None, historical_data=None):
        """
        Analyze a football match using DeepSeek AI.

        Args:
            home_team (dict): Home team information and statistics
            away_team (dict): Away team information and statistics
            match_data (dict): Current match information
            league_data (dict, optional): League context and standings
            historical_data (dict, optional): Historical head-to-head data

        Returns:
            dict: Analysis, predictions, and insights
        """
        prompt = self._build_match_analysis_prompt(
            home_team, away_team, match_data, league_data, historical_data
        )

        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,  # Low temperature for more consistent, focused outputs
            "max_tokens": 2048
        }

        response = await self._make_request("v1/chat/completions", data=data)
        return {
            "analysis": response["choices"][0]["message"]["content"],
            "match_id": match_data.get("id", ""),
            "home_team": home_team.get("name", ""),
            "away_team": away_team.get("name", "")
        }

    async def generate_pre_match_report(self, fixture_data, team_stats, league_context, historical_h2h):
        """
        Generate a comprehensive pre-match report.

        Args:
            fixture_data (dict): Fixture information
            team_stats (dict): Statistics for both teams
            league_context (dict): League standings and context
            historical_h2h (dict): Head-to-head historical data

        Returns:
            dict: Generated pre-match report with insights
        """
        prompt = self._build_pre_match_report_prompt(
            fixture_data, team_stats, league_context, historical_h2h
        )

        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 2500
        }

        response = await self._make_request("v1/chat/completions", data=data)
        return {
            "report": response["choices"][0]["message"]["content"],
            "fixture_id": fixture_data.get("id", ""),
            "home_team": fixture_data.get("home_team", {}).get("name", ""),
            "away_team": fixture_data.get("away_team", {}).get("name", "")
        }

    async def predict_match_result(self, fixture_id, home_team, away_team, team_stats, recent_form, h2h_matches):
        """
        Predict the result of a football match.

        Args:
            fixture_id (int): Fixture ID
            home_team (dict): Home team information
            away_team (dict): Away team information
            team_stats (dict): Statistics for both teams
            recent_form (dict): Recent form for both teams
            h2h_matches (list): Head-to-head matches

        Returns:
            dict: Prediction results with probabilities
        """
        prompt = self._build_prediction_prompt(
            home_team, away_team, team_stats, recent_form, h2h_matches
        )

        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.0,  # Zero temperature for most deterministic predictions
            "response_format": {"type": "json_object"},  # Request structured JSON output
            "max_tokens": 1024
        }

        response = await self._make_request("v1/chat/completions", data=data)
        prediction_text = response["choices"][0]["message"]["content"]

        # Parse JSON response
        try:
            prediction = json.loads(prediction_text)
            prediction["fixture_id"] = fixture_id
            return prediction
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            logger.error(f"Failed to parse prediction as JSON: {prediction_text}")
            return {
                "fixture_id": fixture_id,
                "error": "Failed to parse prediction",
                "raw_output": prediction_text
            }

    async def analyze_betting_opportunities(self, fixture_data, odds_data, team_stats, predictions):
        """
        Analyze betting opportunities for a match.

        Args:
            fixture_data (dict): Fixture information
            odds_data (dict): Bookmaker odds
            team_stats (dict): Team statistics
            predictions (dict): Match predictions

        Returns:
            dict: Betting analysis with value bets identification
        """
        prompt = self._build_betting_analysis_prompt(
            fixture_data, odds_data, team_stats, predictions
        )

        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 1500
        }

        response = await self._make_request("v1/chat/completions", data=data)
        return {
            "analysis": response["choices"][0]["message"]["content"],
            "fixture_id": fixture_data.get("id", ""),
            "home_team": fixture_data.get("home_team", {}).get("name", ""),
            "away_team": fixture_data.get("away_team", {}).get("name", "")
        }

    async def chat_with_ai(self, query, context=None):
        """
        User chat interface with the football AI assistant.

        Args:
            query (str): User question
            context (dict, optional): Additional context data

        Returns:
            dict: AI response
        """
        prompt = query
        if context:
            prompt = f"Context information:\n{json.dumps(context, indent=2)}\n\nUser question: {query}"

        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system",
                 "content": "You are a professional football analyst assistant specialized in match analysis, statistics, and betting insights. Provide factual, insightful answers based on data."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }

        response = await self._make_request("v1/chat/completions", data=data)
        return {
            "response": response["choices"][0]["message"]["content"],
            "query": query
        }

    def _build_match_analysis_prompt(self, home_team, away_team, match_data, league_data=None, historical_data=None):
        """Build prompt for match analysis."""
        prompt = f"""Analyze this football match as an expert:

HOME TEAM: {home_team['name']}
AWAY TEAM: {away_team['name']}

MATCH INFORMATION:
{json.dumps(match_data, indent=2)}

HOME TEAM STATISTICS:
{json.dumps(home_team, indent=2)}

AWAY TEAM STATISTICS:
{json.dumps(away_team, indent=2)}
"""

        if league_data:
            prompt += f"""
LEAGUE CONTEXT:
{json.dumps(league_data, indent=2)}
"""

        if historical_data:
            prompt += f"""
HISTORICAL HEAD-TO-HEAD:
{json.dumps(historical_data, indent=2)}
"""

        prompt += """
Please provide a comprehensive analysis including:
1. Team form and performance trends
2. Key statistical insights
3. Tactical analysis based on the data
4. Predicted match dynamics
5. Key players to watch based on statistics
6. Potential match outcome scenarios

Present your analysis in a structured format with clear sections.
"""
        return prompt

    def _build_pre_match_report_prompt(self, fixture_data, team_stats, league_context, historical_h2h):
        """Build prompt for pre-match report generation."""
        prompt = f"""Generate a comprehensive pre-match report for:

{fixture_data['home_team']['name']} vs {fixture_data['away_team']['name']}
Competition: {fixture_data.get('league', {}).get('name', 'Unknown')}
Date: {fixture_data.get('date', 'Upcoming')}

FIXTURE DATA:
{json.dumps(fixture_data, indent=2)}

TEAM STATISTICS:
{json.dumps(team_stats, indent=2)}

LEAGUE CONTEXT:
{json.dumps(league_context, indent=2)}

HEAD-TO-HEAD HISTORY:
{json.dumps(historical_h2h, indent=2)}

Please generate a detailed pre-match report that includes:
1. Team form analysis for both sides
2. Key statistical comparisons
3. Tactical preview and expected formations
4. Key players to watch and their recent performance
5. Historical context and significance of the matchup
6. Match predictions with justification based on data

Format the report in a professional, journalistic style suitable for a sports website or broadcast.
"""
        return prompt

    def _build_prediction_prompt(self, home_team, away_team, team_stats, recent_form, h2h_matches):
        """Build prompt for match prediction."""
        prompt = f"""Predict the result of this football match using data and statistical modeling:

HOME TEAM: {home_team['name']}
AWAY TEAM: {away_team['name']}

TEAM STATISTICS:
{json.dumps(team_stats, indent=2)}

RECENT FORM:
{json.dumps(recent_form, indent=2)}

HEAD-TO-HEAD MATCHES:
{json.dumps(h2h_matches, indent=2)}

Based on this data, provide a prediction with the following probabilities in JSON format:
- Home win probability (percentage)
- Draw probability (percentage)
- Away win probability (percentage)
- Under/Over 2.5 goals probability
- Both teams to score probability
- Most likely exact score

Provide your response as a valid JSON object with these values.
"""
        return prompt

    def _build_betting_analysis_prompt(self, fixture_data, odds_data, team_stats, predictions):
        """Build prompt for betting analysis."""
        prompt = f"""Analyze betting opportunities for this match:

{fixture_data['home_team']['name']} vs {fixture_data['away_team']['name']}
Competition: {fixture_data.get('league', {}).get('name', 'Unknown')}

FIXTURE DATA:
{json.dumps(fixture_data, indent=2)}

BOOKMAKER ODDS:
{json.dumps(odds_data, indent=2)}

TEAM STATISTICS:
{json.dumps(team_stats, indent=2)}

MATCH PREDICTIONS:
{json.dumps(predictions, indent=2)}

Please analyze the betting markets and identify potential value bets, considering:
1. Comparison of your calculated probabilities vs. bookmaker implied probabilities
2. Identification of markets with positive expected value
3. Recommended bets with justification based on statistical analysis
4. Risk assessment for each potential bet
5. Alternative markets worth considering

Focus on finding true value based on data, not just identifying the likely winner.
"""
        return prompt


# Create a singleton instance
deepseek_client = DeepSeekClient()