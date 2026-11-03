// Standalone fallback fixtures for FINN frontend in production / Vercel
// Automatically loaded when the backend is unreachable so the UI always renders complete, high-fidelity intelligence.

import type {
  AlertsResponse,
  AnomaliesResponse,
  AskResponse,
  CommitmentSummaryResponse,
  CompanyCommitmentsResponse,
  DigestResponse,
  FundamentalsHistoryResponse,
  FundamentalsOverview,
  FundamentalsRatiosResponse,
  PortfolioResponse,
  ResearchModuleInfo,
  ResultsFilingsResponse,
} from "./types";

export const FALLBACK_PORTFOLIO: PortfolioResponse = {
  "as_of": "2026-11-03T17:57:20.838517Z",
  "demo_mode": false,
  "data_source": "yfinance",
  "companies": [
    {
      "ticker": "APOLLOHOSP",
      "name": "Apollo Hospitals Enterprise Limited",
      "sector": "Healthcare",
      "latest_close": 8440.0,
      "prev_close": 8459.0,
      "change_pct": -0.22,
      "latest_volume": 462341,
      "vol_ratio_20d": 0.73,
      "as_of_date": "2026-11-03",
      "source": "yfinance:NS",
      "fetched_at": "2026-11-03 17:21:29",
      "is_stale": false,
      "status": "ok"
    },
    {
      "ticker": "BAJFINANCE",
      "name": "Bajaj Finance Limited",
      "sector": "Financial Services",
      "latest_close": 970.0,
      "prev_close": 959.4000244140625,
      "change_pct": 1.1,
      "latest_volume": 7530518,
      "vol_ratio_20d": 0.9,
      "as_of_date": "2026-11-03",
      "source": "yfinance:NS",
      "fetched_at": "2026-11-03 17:21:31",
      "is_stale": false,
      "status": "ok"
    },
    {
      "ticker": "DIXON",
      "name": "Dixon Technologies (India) Limited",
      "sector": "Electronics Manufacturing",
      "latest_close": 12270.0,
      "prev_close": 12319.0,
      "change_pct": -0.4,
      "latest_volume": 528526,
      "vol_ratio_20d": 1.54,
      "as_of_date": "2026-11-03",
      "source": "yfinance:NS",
      "fetched_at": "2026-11-03 17:21:32",
      "is_stale": false,
      "status": "ok"
    },
    {
      "ticker": "HDFCBANK",
      "name": "HDFC Bank Limited",
      "sector": "Banking",
      "latest_close": 725.5,
      "prev_close": 700.0,
      "change_pct": 3.64,
      "latest_volume": 42738372,
      "vol_ratio_20d": 1.42,
      "as_of_date": "2026-11-03",
      "source": "yfinance:NS",
      "fetched_at": "2026-11-03 17:21:33",
      "is_stale": false,
      "status": "ok"
    },
    {
      "ticker": "HINDUNILVR",
      "name": "Hindustan Unilever Limited",
      "sector": "FMCG",
      "latest_close": 1962.800048828125,
      "prev_close": 1898.300048828125,
      "change_pct": 3.4,
      "latest_volume": 1722676,
      "vol_ratio_20d": 1.03,
      "as_of_date": "2026-11-03",
      "source": "yfinance:NS",
      "fetched_at": "2026-11-03 17:21:35",
      "is_stale": false,
      "status": "ok"
    },
    {
      "ticker": "ICICIBANK",
      "name": "ICICI Bank Limited",
      "sector": "Banking",
      "latest_close": 1424.5,
      "prev_close": 1387.4000244140625,
      "change_pct": 2.67,
      "latest_volume": 17496481,
      "vol_ratio_20d": 1.42,
      "as_of_date": "2026-11-03",
      "source": "yfinance:NS",
      "fetched_at": "2026-11-03 17:21:36",
      "is_stale": false,
      "status": "ok"
    },
    {
      "ticker": "INFY",
      "name": "Infosys Limited",
      "sector": "IT Services",
      "latest_close": 1148.0999755859375,
      "prev_close": 1161.0,
      "change_pct": -1.11,
      "latest_volume": 10494010,
      "vol_ratio_20d": 0.63,
      "as_of_date": "2026-11-03",
      "source": "yfinance:NS",
      "fetched_at": "2026-11-03 17:21:37",
      "is_stale": false,
      "status": "ok"
    },
    {
      "ticker": "ITC",
      "name": "ITC Limited",
      "sector": "FMCG & Conglomerate",
      "latest_close": 273.8999938964844,
      "prev_close": 266.3999938964844,
      "change_pct": 2.82,
      "latest_volume": 31520030,
      "vol_ratio_20d": 1.35,
      "as_of_date": "2026-11-03",
      "source": "yfinance:NS",
      "fetched_at": "2026-11-03 17:21:39",
      "is_stale": false,
      "status": "ok"
    },
    {
      "ticker": "LT",
      "name": "Larsen & Toubro Limited",
      "sector": "Infrastructure & Engineering",
      "latest_close": 3948.199951171875,
      "prev_close": 3939.89990234375,
      "change_pct": 0.21,
      "latest_volume": 2152853,
      "vol_ratio_20d": 1.03,
      "as_of_date": "2026-11-03",
      "source": "yfinance:NS",
      "fetched_at": "2026-11-03 17:21:40",
      "is_stale": false,
      "status": "ok"
    },
    {
      "ticker": "M&M",
      "name": "Mahindra & Mahindra Limited",
      "sector": "Automobile",
      "latest_close": 2908.0,
      "prev_close": 2868.800048828125,
      "change_pct": 1.37,
      "latest_volume": 3056309,
      "vol_ratio_20d": 1.33,
      "as_of_date": "2026-11-03",
      "source": "yfinance:NS",
      "fetched_at": "2026-11-03 17:21:42",
      "is_stale": false,
      "status": "ok"
    },
    {
      "ticker": "MARUTI",
      "name": "Maruti Suzuki India Limited",
      "sector": "Automobile",
      "latest_close": 11869.0,
      "prev_close": 11672.0,
      "change_pct": 1.69,
      "latest_volume": 363540,
      "vol_ratio_20d": 0.78,
      "as_of_date": "2026-11-03",
      "source": "yfinance:NS",
      "fetched_at": "2026-11-03 17:21:43",
      "is_stale": false,
      "status": "ok"
    },
    {
      "ticker": "PERSISTENT",
      "name": "Persistent Systems Limited",
      "sector": "IT Services",
      "latest_close": 6097.0,
      "prev_close": 6051.0,
      "change_pct": 0.76,
      "latest_volume": 388520,
      "vol_ratio_20d": 0.48,
      "as_of_date": "2026-11-03",
      "source": "yfinance:NS",
      "fetched_at": "2026-11-03 17:21:45",
      "is_stale": false,
      "status": "ok"
    },
    {
      "ticker": "POLYCAB",
      "name": "Polycab India Limited",
      "sector": "Electrical Equipment",
      "latest_close": 7837.0,
      "prev_close": 7920.0,
      "change_pct": -1.05,
      "latest_volume": 241172,
      "vol_ratio_20d": 0.54,
      "as_of_date": "2026-11-03",
      "source": "yfinance:NS",
      "fetched_at": "2026-11-03 17:21:46",
      "is_stale": false,
      "status": "ok"
    },
    {
      "ticker": "RELIANCE",
      "name": "Reliance Industries Limited",
      "sector": "Energy & Conglomerate",
      "latest_close": 1307.9000244140625,
      "prev_close": 1300.0,
      "change_pct": 0.61,
      "latest_volume": 42318217,
      "vol_ratio_20d": 2.27,
      "as_of_date": "2026-11-03",
      "source": "yfinance:NS",
      "fetched_at": "2026-11-03 17:21:47",
      "is_stale": false,
      "status": "ok"
    },
    {
      "ticker": "SBIN",
      "name": "State Bank of India",
      "sector": "Banking",
      "latest_close": 970.25,
      "prev_close": 987.0,
      "change_pct": -1.7,
      "latest_volume": 27953749,
      "vol_ratio_20d": 3.08,
      "as_of_date": "2026-11-03",
      "source": "yfinance:NS",
      "fetched_at": "2026-11-03 17:21:48",
      "is_stale": false,
      "status": "ok"
    },
    {
      "ticker": "SUNPHARMA",
      "name": "Sun Pharmaceutical Industries Limited",
      "sector": "Pharmaceuticals",
      "latest_close": 1769.9000244140625,
      "prev_close": 1770.0,
      "change_pct": -0.01,
      "latest_volume": 2646614,
      "vol_ratio_20d": 1.56,
      "as_of_date": "2026-11-03",
      "source": "yfinance:NS",
      "fetched_at": "2026-11-03 17:21:50",
      "is_stale": false,
      "status": "ok"
    },
    {
      "ticker": "SUZLON",
      "name": "Suzlon Energy Limited",
      "sector": "Renewable Energy",
      "latest_close": 35.75,
      "prev_close": 35.25,
      "change_pct": 1.42,
      "latest_volume": 63415991,
      "vol_ratio_20d": 0.69,
      "as_of_date": "2026-11-03",
      "source": "yfinance:NS",
      "fetched_at": "2026-11-03 17:21:51",
      "is_stale": false,
      "status": "ok"
    },
    {
      "ticker": "TCS",
      "name": "Tata Consultancy Services Limited",
      "sector": "IT Services",
      "latest_close": 2499.10009765625,
      "prev_close": 2501.699951171875,
      "change_pct": -0.1,
      "latest_volume": 3485800,
      "vol_ratio_20d": 0.59,
      "as_of_date": "2026-11-03",
      "source": "yfinance:NS",
      "fetched_at": "2026-11-03 17:21:53",
      "is_stale": false,
      "status": "ok"
    },
    {
      "ticker": "TITAN",
      "name": "Titan Company Limited",
      "sector": "Consumer Goods & Retail",
      "latest_close": 4562.0,
      "prev_close": 4476.2998046875,
      "change_pct": 1.91,
      "latest_volume": 773149,
      "vol_ratio_20d": 0.96,
      "as_of_date": "2026-11-03",
      "source": "yfinance:NS",
      "fetched_at": "2026-11-03 17:21:54",
      "is_stale": false,
      "status": "ok"
    },
    {
      "ticker": "TRENT",
      "name": "Trent Limited",
      "sector": "Retail",
      "latest_close": 3036.5,
      "prev_close": 3046.39990234375,
      "change_pct": -0.32,
      "latest_volume": 850011,
      "vol_ratio_20d": 0.64,
      "as_of_date": "2026-11-03",
      "source": "yfinance:NS",
      "fetched_at": "2026-11-03 17:21:55",
      "is_stale": false,
      "status": "ok"
    }
  ]
};

export const FALLBACK_DIGEST_24H: DigestResponse = {
  "window": "24h",
  "from_at": "2026-11-02T17:57:20.874077Z",
  "to_at": "2026-11-03T17:57:20.874077Z",
  "as_of": "2026-11-03T17:57:20.874077Z",
  "demo_mode": false,
  "status": "ok",
  "last_refresh": "2026-11-03T17:21:55Z",
  "items": [
    {
      "id": "announcement:06699ded4bb5c6c73782d9bfcf6e461c9285c82362e8670dec9dbb53c9e5a2ff",
      "ticker": "SBIN",
      "company_name": "State Bank of India",
      "kind": "filing",
      "category": "investor_meetings",
      "headline": "Analysts/Institutional Investor Meet/Con. Call Updates",
      "summary": "Investor or analyst meeting notice",
      "priority": "low",
      "occurred_at": "2026-11-03T15:00:22Z",
      "citations": [
        {
          "document": "106842909",
          "locator": "2026-11-03T15:00:22Z",
          "quote": "Analysts/Institutional Investor Meet/Con. Call Updates"
        }
      ],
      "materiality_score": 2.0,
      "source_reference": "106842909",
      "attachment_url": "https://nsearchives.nseindia.com/corporate/SBIN_03112026202912_BSE_NSE_Post_Anlyst_recording_03112026.pdf",
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-03T17:06:53Z",
      "demo_mode": false,
      "rank_score": 62.99,
      "rank_reasons": [
        "Source materiality 2/10",
        "Category significance 3/9",
        "Company is marked in the portfolio",
        "Recency 9.99/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "raw_category": null,
        "materiality_reason": "Investor or analyst meeting notice",
        "duplicate_sources": [
          "106842909",
          "106835011"
        ],
        "duplicate_count": 3
      }
    },
    {
      "id": "announcement:97824ada0035c4483ece82d21e24ff8ab3c5197af68a8fb910d7dd7bb772e0ae",
      "ticker": "SBIN",
      "company_name": "State Bank of India",
      "kind": "filing",
      "category": "investor_meetings",
      "headline": "Investor Presentation",
      "summary": "Investor or analyst meeting notice",
      "priority": "low",
      "occurred_at": "2026-11-03T08:29:35Z",
      "citations": [
        {
          "document": "106841606",
          "locator": "2026-11-03T08:29:35Z",
          "quote": "Investor Presentation"
        }
      ],
      "materiality_score": 2.0,
      "source_reference": "106841606",
      "attachment_url": "https://nsearchives.nseindia.com/corporate/SBIN_03112026135925_Presentation.pdf",
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-03T17:06:53Z",
      "demo_mode": false,
      "rank_score": 62.96,
      "rank_reasons": [
        "Source materiality 2/10",
        "Category significance 3/9",
        "Company is marked in the portfolio",
        "Recency 9.96/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "raw_category": null,
        "materiality_reason": "Investor or analyst meeting notice"
      }
    },
    {
      "id": "announcement:aec1fa45d96cdab4ca4df1a47cea6bec54606b5cda69f709ae1535f6e16d7a85",
      "ticker": "DIXON",
      "company_name": "Dixon Technologies (India) Limited",
      "kind": "filing",
      "category": "investor_meetings",
      "headline": "Analysts/Institutional Investor Meet/Con. Call Updates",
      "summary": "Investor or analyst meeting notice",
      "priority": "low",
      "occurred_at": "2026-11-03T05:54:09Z",
      "citations": [
        {
          "document": "106841276",
          "locator": "2026-11-03T05:54:09Z",
          "quote": "Analysts/Institutional Investor Meet/Con. Call Updates"
        }
      ],
      "materiality_score": 2.0,
      "source_reference": "106841276",
      "attachment_url": "https://nsearchives.nseindia.com/corporate/DIXON_03112026112356_InvestorMeetOutcome031102026.pdf",
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-03T17:06:24Z",
      "demo_mode": false,
      "rank_score": 62.94,
      "rank_reasons": [
        "Source materiality 2/10",
        "Category significance 3/9",
        "Company is marked in the portfolio",
        "Recency 9.94/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "raw_category": null,
        "materiality_reason": "Investor or analyst meeting notice",
        "duplicate_sources": [
          "106841276",
          "106837485"
        ],
        "duplicate_count": 4
      }
    },
    {
      "id": "announcement:a6a4105f0d55e94be19923144d51c4499018462f7e55fa2a41478bcc4f7e8abe",
      "ticker": "SBIN",
      "company_name": "State Bank of India",
      "kind": "filing",
      "category": "press_release",
      "headline": "Press Release",
      "summary": "General press or media release; conservative default",
      "priority": "low",
      "occurred_at": "2026-11-03T08:29:35Z",
      "citations": [
        {
          "document": "106841605",
          "locator": "2026-11-03T08:29:35Z",
          "quote": "Press Release"
        }
      ],
      "materiality_score": 2.0,
      "source_reference": "106841605",
      "attachment_url": "https://nsearchives.nseindia.com/corporate/SBIN_03112026135813_PressRelease.pdf",
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-03T17:06:53Z",
      "demo_mode": false,
      "rank_score": 57.96,
      "rank_reasons": [
        "Source materiality 2/10",
        "Category significance 2/9",
        "Company is marked in the portfolio",
        "Recency 9.96/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "raw_category": null,
        "materiality_reason": "General press or media release; conservative default"
      }
    },
    {
      "id": "anomaly:fc9b53dc1fbb860bfbc64cbe",
      "ticker": "SBIN",
      "company_name": "State Bank of India",
      "kind": "anomaly",
      "category": "volume_anomaly",
      "headline": "Trading anomaly detected",
      "summary": "Volume 3.1x its 20-day average",
      "priority": "medium",
      "occurred_at": "2026-11-03T00:00:00Z",
      "citations": [],
      "materiality_score": null,
      "source_reference": "prices:2026-11-03",
      "attachment_url": null,
      "data_source": "yfinance",
      "source": "yfinance",
      "fetched_at": "2026-11-03T00:00:00Z",
      "demo_mode": false,
      "rank_score": 57.92,
      "rank_reasons": [
        "Category significance 6/9",
        "Company is marked in the portfolio",
        "Recency 9.92/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "anomalies": [
          {
            "type": "volume_spike",
            "observed_value": 3.0791365974548848,
            "threshold_value": 2.0,
            "unit": "multiple"
          }
        ]
      }
    },
    {
      "id": "anomaly:f580370cc10d346ac2c49d0a",
      "ticker": "HDFCBANK",
      "company_name": "HDFC Bank Limited",
      "kind": "anomaly",
      "category": "price_anomaly",
      "headline": "Trading anomaly detected",
      "summary": "price +3.6%",
      "priority": "medium",
      "occurred_at": "2026-11-03T00:00:00Z",
      "citations": [],
      "materiality_score": null,
      "source_reference": "prices:2026-11-03",
      "attachment_url": null,
      "data_source": "yfinance",
      "source": "yfinance",
      "fetched_at": "2026-11-03T00:00:00Z",
      "demo_mode": false,
      "rank_score": 57.92,
      "rank_reasons": [
        "Category significance 6/9",
        "Company is marked in the portfolio",
        "Recency 9.92/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "anomalies": [
          {
            "type": "price_move",
            "observed_value": 3.6428571428571477,
            "threshold_value": 3.0,
            "unit": "percent"
          }
        ]
      }
    },
    {
      "id": "anomaly:d2efd7433b847b4117a670af",
      "ticker": "HINDUNILVR",
      "company_name": "Hindustan Unilever Limited",
      "kind": "anomaly",
      "category": "price_anomaly",
      "headline": "Trading anomaly detected",
      "summary": "price +3.4%",
      "priority": "medium",
      "occurred_at": "2026-11-03T00:00:00Z",
      "citations": [],
      "materiality_score": null,
      "source_reference": "prices:2026-11-03",
      "attachment_url": null,
      "data_source": "yfinance",
      "source": "yfinance",
      "fetched_at": "2026-11-03T00:00:00Z",
      "demo_mode": false,
      "rank_score": 57.92,
      "rank_reasons": [
        "Category significance 6/9",
        "Company is marked in the portfolio",
        "Recency 9.92/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "anomalies": [
          {
            "type": "price_move",
            "observed_value": 3.3977768709334333,
            "threshold_value": 3.0,
            "unit": "percent"
          }
        ]
      }
    },
    {
      "id": "anomaly:3be8b98a0fc1367a27348df3",
      "ticker": "RELIANCE",
      "company_name": "Reliance Industries Limited",
      "kind": "anomaly",
      "category": "volume_anomaly",
      "headline": "Trading anomaly detected",
      "summary": "Volume 2.3x its 20-day average",
      "priority": "medium",
      "occurred_at": "2026-11-03T00:00:00Z",
      "citations": [],
      "materiality_score": null,
      "source_reference": "prices:2026-11-03",
      "attachment_url": null,
      "data_source": "yfinance",
      "source": "yfinance",
      "fetched_at": "2026-11-03T00:00:00Z",
      "demo_mode": false,
      "rank_score": 57.92,
      "rank_reasons": [
        "Category significance 6/9",
        "Company is marked in the portfolio",
        "Recency 9.92/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "anomalies": [
          {
            "type": "volume_spike",
            "observed_value": 2.26652220228089,
            "threshold_value": 2.0,
            "unit": "multiple"
          }
        ]
      }
    },
    {
      "id": "routine:4d08f42f4178eafd10d77977",
      "ticker": "TCS",
      "company_name": "Tata Consultancy Services Limited",
      "kind": "filing",
      "category": "unclassified",
      "headline": "5 routine unclassified disclosures",
      "summary": "5 lower-materiality disclosures of this category are grouped here; expand for the individual filings.",
      "priority": "low",
      "occurred_at": "2026-11-03T13:22:12Z",
      "citations": [
        {
          "document": "106842587",
          "locator": "2026-11-03T13:22:12Z",
          "quote": "Copy of Newspaper Publication"
        },
        {
          "document": "106821698",
          "locator": "2026-10-19T06:00:07Z",
          "quote": "Updates"
        },
        {
          "document": "106818480",
          "locator": "2026-10-15T08:00:23Z",
          "quote": "General Updates"
        },
        {
          "document": "106811188",
          "locator": "2026-10-08T10:12:03Z",
          "quote": "Dividend"
        },
        {
          "document": "106811186",
          "locator": "2026-10-08T10:10:12Z",
          "quote": "Outcome of Board Meeting"
        }
      ],
      "materiality_score": 1.0,
      "source_reference": null,
      "attachment_url": null,
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-03T17:07:01Z",
      "demo_mode": false,
      "rank_score": 40.98,
      "rank_reasons": [
        "Source materiality 1/10",
        "Category significance 1/9",
        "Company is marked in the portfolio",
        "Recency 9.98/10",
        "Supporting details available"
      ],
      "collapsed_count": 5,
      "supporting_details": {
        "grouped_events": [
          {
            "id": "announcement:dc90d6c0d5847c45f9c6ba19e6565ee8733b07b8a58e2370e9e4dae393cde890",
            "headline": "Copy of Newspaper Publication",
            "occurred_at": "2026-11-03T13:22:12Z",
            "source_reference": "106842587",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/TCS_CORPCS_03112026185113_SEInt3112026_signed.pdf"
          },
          {
            "id": "announcement:fb8b24c80d46267f92c23546c8cfc268aa7fd60c1b0ccd00ed30a3cddf8bdd4c",
            "headline": "Updates",
            "occurred_at": "2026-10-19T06:00:07Z",
            "source_reference": "106821698",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/TCS_CORPCS_19102026112258_PR_19Oct26_signed.pdf"
          },
          {
            "id": "announcement:0bd3d23b541d1327346d9c495facfc48a6fb797ae41fec6a2dab1e8f7a0925bc",
            "headline": "General Updates",
            "occurred_at": "2026-10-15T08:00:23Z",
            "source_reference": "106818480",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/TCS_CORPCS_15102026133009_SEInt15102026.pdf"
          },
          {
            "id": "announcement:d14fcac4e33e4a7b17134897fc004852343b0646d47b73e4d6c96dfc3f2e3590",
            "headline": "Dividend",
            "occurred_at": "2026-10-08T10:12:03Z",
            "source_reference": "106811188",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/TCS_CORPCS_08102026154152_Post_BM_SE_Letter_fin.pdf"
          },
          {
            "id": "announcement:8300ed1e4c7b3e4630a06dabdd2e92982fb10083e82b222dedf9d5c5f9378073",
            "headline": "Outcome of Board Meeting",
            "occurred_at": "2026-10-08T10:10:12Z",
            "source_reference": "106811186",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/TCS_CORPCS_08102026153124_Post_BM_SE_Letter_fin.pdf"
          }
        ]
      }
    },
    {
      "id": "routine:8d641dbd9ea956f4e16c29c5",
      "ticker": "DIXON",
      "company_name": "Dixon Technologies (India) Limited",
      "kind": "filing",
      "category": "unclassified",
      "headline": "7 routine unclassified disclosures",
      "summary": "7 lower-materiality disclosures of this category are grouped here; expand for the individual filings.",
      "priority": "low",
      "occurred_at": "2026-11-03T12:00:12Z",
      "citations": [
        {
          "document": "106842234",
          "locator": "2026-11-03T12:00:12Z",
          "quote": "Updates"
        },
        {
          "document": "106838529",
          "locator": "2026-10-31T14:02:44Z",
          "quote": "Copy of Newspaper Publication"
        },
        {
          "document": "106836531",
          "locator": "2026-10-30T10:40:12Z",
          "quote": "Change in Management"
        },
        {
          "document": "106836523",
          "locator": "2026-10-30T10:37:23Z",
          "quote": "Outcome of Board Meeting"
        },
        {
          "document": "106817628",
          "locator": "2026-10-14T12:55:23Z",
          "quote": "General Updates"
        },
        {
          "document": "106812913",
          "locator": "2026-10-09T12:53:50Z",
          "quote": "Certificate under SEBI (Depositories and Participants) Regulations, 2018"
        },
        {
          "document": "106809698",
          "locator": "2026-10-07T09:31:51Z",
          "quote": "Agreements"
        }
      ],
      "materiality_score": 1.0,
      "source_reference": null,
      "attachment_url": null,
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-03T17:06:24Z",
      "demo_mode": false,
      "rank_score": 40.97,
      "rank_reasons": [
        "Source materiality 1/10",
        "Category significance 1/9",
        "Company is marked in the portfolio",
        "Recency 9.97/10",
        "Supporting details available"
      ],
      "collapsed_count": 7,
      "supporting_details": {
        "grouped_events": [
          {
            "id": "announcement:4b200d5b9d340d9834bdaa598e4f1ea5df4d6e15fd8cfddeda4359ff7b9ff027",
            "headline": "Updates",
            "occurred_at": "2026-11-03T12:00:12Z",
            "source_reference": "106842234",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/DIXON_03112026172946_Regulation30DisclosureRTAAddress.pdf"
          },
          {
            "id": "announcement:a624fb225b5fbc561d0936c82080f5823735e7a8a8c3bf8054af0c2d8d0a0968",
            "headline": "Copy of Newspaper Publication",
            "occurred_at": "2026-10-31T14:02:44Z",
            "source_reference": "106838529",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/DIXON_31102026192630_NewspaperAdvertisement31101026.pdf"
          },
          {
            "id": "announcement:810c7bad8e3bd18f141e52512c2acc78282050de44d5cc09e8c6f11ddf5c7bad",
            "headline": "Change in Management",
            "occurred_at": "2026-10-30T10:40:12Z",
            "source_reference": "106836531",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/DIXON_30102026160939_Outcome30102026.pdf"
          },
          {
            "id": "announcement:54fc761e6b0be6b9c95687d8f70c096770cf32f9f5367eddb438bff1e06fe69f",
            "headline": "Outcome of Board Meeting",
            "occurred_at": "2026-10-30T10:37:23Z",
            "source_reference": "106836523",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/DIXON_30102026160547_Outcome30102026.pdf"
          },
          {
            "id": "announcement:42c265c5b0426030ffdbf1e9e7ccd72a5e642581fa10be69e5da88630c158158",
            "headline": "General Updates",
            "occurred_at": "2026-10-14T12:55:23Z",
            "source_reference": "106817628",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/DIXON_14102026182232_ESGRatingDisclousureCrisil14102026.pdf"
          },
          {
            "id": "announcement:aa004b5d9d683b1b761a642c80d6782dc4567dcaa92c0e2a25de5907bd9c308f",
            "headline": "Certificate under SEBI (Depositories and Participants) Regulations, 2018",
            "occurred_at": "2026-10-09T12:53:50Z",
            "source_reference": "106812913",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/DIXON_09102026182235_Reg74_5_Disclosure09102026.pdf"
          },
          {
            "id": "announcement:dfc57b4eb4ebb8f51a000d56601fdee6d0a82fe98ee37a062a18a88a294418d4",
            "headline": "Agreements",
            "occurred_at": "2026-10-07T09:31:51Z",
            "source_reference": "106809698",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/DIXON_07102026150006_Regulation30_DisclosureGemtek07102026.pdf"
          }
        ]
      }
    },
    {
      "id": "routine:4ed801dddb456c61ca31b3a2",
      "ticker": "M&M",
      "company_name": "Mahindra & Mahindra Limited",
      "kind": "filing",
      "category": "unclassified",
      "headline": "5 routine unclassified disclosures",
      "summary": "5 lower-materiality disclosures of this category are grouped here; expand for the individual filings.",
      "priority": "low",
      "occurred_at": "2026-11-03T10:37:13Z",
      "citations": [
        {
          "document": "106841911",
          "locator": "2026-11-03T10:37:13Z",
          "quote": "Updates"
        },
        {
          "document": "106838749",
          "locator": "2026-11-01T04:45:10Z",
          "quote": "Monthly Business Updates"
        },
        {
          "document": "106820992",
          "locator": "2026-10-17T07:08:10Z",
          "quote": "General Updates"
        },
        {
          "document": "106820100",
          "locator": "2026-10-16T09:52:12Z",
          "quote": "Copy of Newspaper Publication"
        },
        {
          "document": "106813278",
          "locator": "2026-10-09T17:50:18Z",
          "quote": "Sale or disposal"
        }
      ],
      "materiality_score": 1.0,
      "source_reference": null,
      "attachment_url": null,
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-03T17:06:40Z",
      "demo_mode": false,
      "rank_score": 40.97,
      "rank_reasons": [
        "Source materiality 1/10",
        "Category significance 1/9",
        "Company is marked in the portfolio",
        "Recency 9.97/10",
        "Supporting details available"
      ],
      "collapsed_count": 5,
      "supporting_details": {
        "grouped_events": [
          {
            "id": "announcement:ade4d110f8f568f765beaf1f775b78a2f8e922fe30c4c410bcca5d4308a7a8c1",
            "headline": "Updates",
            "occurred_at": "2026-11-03T10:37:13Z",
            "source_reference": "106841911",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/Deepak_03112026160659_SE_Intimation_Change_of_Kfintech_Corporate_Office.pdf"
          },
          {
            "id": "announcement:ebd386af19decd979c57d12e473b92b343500194520ff3ac2e5f826ea5eb2c17",
            "headline": "Monthly Business Updates",
            "occurred_at": "2026-11-01T04:45:10Z",
            "source_reference": "106838749",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/ferozebaria_01112026101454_SEIntimationNovember2026PR.pdf"
          },
          {
            "id": "announcement:be3034693e85aafbde09773dcfd1dd9c91b9b0db2b53438930967f6e7cdb34d5",
            "headline": "General Updates",
            "occurred_at": "2026-10-17T07:08:10Z",
            "source_reference": "106820992",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/AmitDodani_17102026123753_SE_Intimation_NDET_Dilution.pdf"
          },
          {
            "id": "announcement:5cb86c8153682035f28c3b0863267bde1410e312deab5312576c89448a77481a",
            "headline": "Copy of Newspaper Publication",
            "occurred_at": "2026-10-16T09:52:12Z",
            "source_reference": "106820100",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/Deepak_16102026152139_SE_INTIMATION_LOST_OF_SHARE_CERTIFICATE_2026_-_OCT_.pdf"
          },
          {
            "id": "announcement:5e723eb001a798f7d30c7d94802afd7260a783ff4575655cac14d6f418e683df",
            "headline": "Sale or disposal",
            "occurred_at": "2026-10-09T17:50:18Z",
            "source_reference": "106813278",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/AmitDodani_09102026232007_Novavayu_SE_Intimation_Investment_Agreement_Revised.pdf"
          }
        ]
      }
    },
    {
      "id": "routine:0412468cd0fb5b0cfa96cae5",
      "ticker": "SBIN",
      "company_name": "State Bank of India",
      "kind": "filing",
      "category": "unclassified",
      "headline": "5 routine unclassified disclosures",
      "summary": "5 lower-materiality disclosures of this category are grouped here; expand for the individual filings.",
      "priority": "low",
      "occurred_at": "2026-11-03T09:42:51Z",
      "citations": [
        {
          "document": "106841767",
          "locator": "2026-11-03T09:42:51Z",
          "quote": "Statement of deviation(s) or variation(s) under Reg. 32"
        },
        {
          "document": "106841577",
          "locator": "2026-11-03T08:17:53Z",
          "quote": "Outcome of Board Meeting"
        },
        {
          "document": "106822872",
          "locator": "2026-10-21T03:21:09Z",
          "quote": "General Updates"
        },
        {
          "document": "106812599",
          "locator": "2026-10-09T10:20:05Z",
          "quote": "Copy of Newspaper Publication"
        },
        {
          "document": "106811266",
          "locator": "2026-10-08T10:57:09Z",
          "quote": "Certificate under SEBI (Depositories and Participants) Regulations, 2018"
        }
      ],
      "materiality_score": 1.0,
      "source_reference": null,
      "attachment_url": null,
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-03T17:06:53Z",
      "demo_mode": false,
      "rank_score": 40.96,
      "rank_reasons": [
        "Source materiality 1/10",
        "Category significance 1/9",
        "Company is marked in the portfolio",
        "Recency 9.96/10",
        "Supporting details available"
      ],
      "collapsed_count": 5,
      "supporting_details": {
        "grouped_events": [
          {
            "id": "announcement:bb7749101ebf339cd921cf671c097eb8b39a637f8482fae3a00dc79af5f3f473",
            "headline": "Statement of deviation(s) or variation(s) under Reg. 32",
            "occurred_at": "2026-11-03T09:42:51Z",
            "source_reference": "106841767",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/SBIN_03112026151233_DeviationUtilisation.pdf"
          },
          {
            "id": "announcement:42c320142d553329d4f60fa54bda9fb177ef9736808f2ee1585d4630d4a94143",
            "headline": "Outcome of Board Meeting",
            "occurred_at": "2026-11-03T08:17:53Z",
            "source_reference": "106841577",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/SBIN_03112026134649_FR_DSC.pdf"
          },
          {
            "id": "announcement:673acc75f4c46e847249e5b0f5e300aa242abd8296137f86d3a76ca8b8e34389",
            "headline": "General Updates",
            "occurred_at": "2026-10-21T03:21:09Z",
            "source_reference": "106822872",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/SBIN_21102026084938_BSE_NSE_21102026.pdf"
          },
          {
            "id": "announcement:8b402f02776391a657cb6217fcad70c358dab38b01bff44a351d9e1803556d41",
            "headline": "Copy of Newspaper Publication",
            "occurred_at": "2026-10-09T10:20:05Z",
            "source_reference": "106812599",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/SBIN_09102026154949_NewsPaper09102026.pdf"
          },
          {
            "id": "announcement:db81345dcca3b1058c37831652a0027f94ec8f062ce152f0d3d960e99e43fca6",
            "headline": "Certificate under SEBI (Depositories and Participants) Regulations, 2018",
            "occurred_at": "2026-10-08T10:57:09Z",
            "source_reference": "106811266",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/SBIN_08102026162654_BSE_NSE_74_5__08102026.pdf"
          }
        ]
      }
    },
    {
      "id": "routine:2a999ec3c64e4729a3249d46",
      "ticker": "POLYCAB",
      "company_name": "Polycab India Limited",
      "kind": "filing",
      "category": "unclassified",
      "headline": "5 routine unclassified disclosures",
      "summary": "5 lower-materiality disclosures of this category are grouped here; expand for the individual filings.",
      "priority": "low",
      "occurred_at": "2026-11-03T10:31:15Z",
      "citations": [
        {
          "document": "106841885",
          "locator": "2026-11-03T10:31:15Z",
          "quote": "ESOP/ESOS/ESPS"
        },
        {
          "document": "106836029",
          "locator": "2026-10-30T06:50:09Z",
          "quote": "Corporate Insolvency Resolution Process"
        },
        {
          "document": "106832611",
          "locator": "2026-10-28T12:13:39Z",
          "quote": "General Updates"
        },
        {
          "document": "106830830",
          "locator": "2026-10-27T13:12:35Z",
          "quote": "Certificate under SEBI (Depositories and Participants) Regulations, 2018"
        },
        {
          "document": "106818441",
          "locator": "2026-10-15T07:28:53Z",
          "quote": "Outcome of Board Meeting"
        }
      ],
      "materiality_score": 0.0,
      "source_reference": null,
      "attachment_url": null,
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-03T17:06:48Z",
      "demo_mode": false,
      "rank_score": 30.97,
      "rank_reasons": [
        "Source materiality 0/10",
        "Category significance 1/9",
        "Company is marked in the portfolio",
        "Recency 9.97/10",
        "Supporting details available"
      ],
      "collapsed_count": 5,
      "supporting_details": {
        "grouped_events": [
          {
            "id": "announcement:97374c74fa54f04517e5121fface7d001494c69c9eb112a7b79631b38fb4b025",
            "headline": "ESOP/ESOS/ESPS",
            "occurred_at": "2026-11-03T10:31:15Z",
            "source_reference": "106841885",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/POLYCAB_03112026160106_IntimationtoStockexchange.pdf"
          },
          {
            "id": "announcement:bbab2682cb0b13eafbec95caa127a382adb01315d272acc7a01704f386d47c4a",
            "headline": "Corporate Insolvency Resolution Process",
            "occurred_at": "2026-10-30T06:50:09Z",
            "source_reference": "106836029",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/POLYCAB_30102026121954_SECIRP30102026.pdf"
          },
          {
            "id": "announcement:f1a4f416705f784e23f13c1b3458bcbb7e76a42e5c09c031e99ec30b151bac31",
            "headline": "General Updates",
            "occurred_at": "2026-10-28T12:13:39Z",
            "source_reference": "106832611",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/POLYCAB_28102026174326_Intimationtostockexchange.pdf"
          },
          {
            "id": "announcement:d1a2585adffafdaf06a59b6c8fb052103ac91ebfd8fcff91c60c28f5c67a42d0",
            "headline": "Certificate under SEBI (Depositories and Participants) Regulations, 2018",
            "occurred_at": "2026-10-27T13:12:35Z",
            "source_reference": "106830830",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/POLYCAB_27102026184209_IntimationtoStockExchange.pdf"
          },
          {
            "id": "announcement:bccafdb36599a22307a415c5dfa1e79bbe79e2a39558e9a6d86cfd320efc9889",
            "headline": "Outcome of Board Meeting",
            "occurred_at": "2026-10-15T07:28:53Z",
            "source_reference": "106818441",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/POLYCAB_15102026125737_OutcomeofBoardMeeting.pdf"
          }
        ]
      }
    },
    {
      "id": "routine:665de5315ce6ad3ee3d413bb",
      "ticker": "ICICIBANK",
      "company_name": "ICICI Bank Limited",
      "kind": "filing",
      "category": "unclassified",
      "headline": "4 routine unclassified disclosures",
      "summary": "4 lower-materiality disclosures of this category are grouped here; expand for the individual filings.",
      "priority": "low",
      "occurred_at": "2026-11-03T04:54:40Z",
      "citations": [
        {
          "document": "106841159",
          "locator": "2026-11-03T04:54:40Z",
          "quote": "ESOP/ESOS/ESPS"
        },
        {
          "document": "106838744",
          "locator": "2026-11-01T04:13:51Z",
          "quote": "General Updates"
        },
        {
          "document": "106821131",
          "locator": "2026-10-17T09:58:05Z",
          "quote": "Outcome of Board Meeting"
        },
        {
          "document": "106811462",
          "locator": "2026-10-08T12:07:19Z",
          "quote": "Certificate under SEBI (Depositories and Participants) Regulations, 2018"
        }
      ],
      "materiality_score": 0.0,
      "source_reference": null,
      "attachment_url": null,
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-03T17:06:31Z",
      "demo_mode": false,
      "rank_score": 30.94,
      "rank_reasons": [
        "Source materiality 0/10",
        "Category significance 1/9",
        "Company is marked in the portfolio",
        "Recency 9.94/10",
        "Supporting details available"
      ],
      "collapsed_count": 4,
      "supporting_details": {
        "grouped_events": [
          {
            "id": "announcement:90e38a8d92bcbc4dd5fc273c4e013091b1b53293ef9379cee48ae4fa239df895",
            "headline": "ESOP/ESOS/ESPS",
            "occurred_at": "2026-11-03T04:54:40Z",
            "source_reference": "106841159",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/ICICIBANK1_03112026102424_Lettertoexchange.pdf"
          },
          {
            "id": "announcement:80e3eee157538e583d495d57685d0f71fba5535fa8365966b67e1dcc09bd06f0",
            "headline": "General Updates",
            "occurred_at": "2026-11-01T04:13:51Z",
            "source_reference": "106838744",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/ICICI2022_01112026094235_BSENSE01112026.pdf"
          },
          {
            "id": "announcement:3b0f05c5fa454dc57da24e048e08b08549eb662f9b711d45326c47931685a37c",
            "headline": "Outcome of Board Meeting",
            "occurred_at": "2026-10-17T09:58:05Z",
            "source_reference": "106821131",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/ICICI2022_17102026152608_NSEBSE17102026.pdf"
          },
          {
            "id": "announcement:61b7970c8448617f1dd5e9fea3af8b1918282272963a205f74e1341b1ed1600b",
            "headline": "Certificate under SEBI (Depositories and Participants) Regulations, 2018",
            "occurred_at": "2026-10-08T12:07:19Z",
            "source_reference": "106811462",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/ICICIBANK1_08102026173642_Regulation_74_5__Certificate_NSE_BSE_20260930-BONDS.pdf"
          }
        ]
      }
    }
  ],
  "collapsed_count": 226,
  "total_count": 14,
  "limit": 50,
  "offset": 0,
  "sort": "relevance"
};

export const FALLBACK_DIGEST_7D: DigestResponse = {
  "window": "7d",
  "from_at": "2026-10-27T17:57:20.922432Z",
  "to_at": "2026-11-03T17:57:20.922432Z",
  "as_of": "2026-11-03T17:57:20.922432Z",
  "demo_mode": false,
  "status": "ok",
  "last_refresh": "2026-11-03T17:21:55Z",
  "items": [
    {
      "id": "announcement:a8569f7ec2bf38753c0a5ae99c257a720dd03615b125a62fdb149e6f3d4e4a42",
      "ticker": "ITC",
      "company_name": "ITC Limited",
      "kind": "filing",
      "category": "M&A",
      "headline": "Amalgamation/Merger",
      "summary": "Amalgamation/Merger",
      "priority": "high",
      "occurred_at": "2026-11-02T13:15:24Z",
      "citations": [
        {
          "document": "106840382",
          "locator": "2026-11-02T13:15:24Z",
          "quote": "Amalgamation/Merger"
        }
      ],
      "materiality_score": 8.0,
      "source_reference": "106840382",
      "attachment_url": "https://nsearchives.nseindia.com/corporate/ITC_02112026184512_SE_Sproutlife_.pdf",
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:52:00Z",
      "demo_mode": false,
      "rank_score": 152.87,
      "rank_reasons": [
        "Source materiality 8/10",
        "Category significance 9/9",
        "Company is marked in the portfolio",
        "Recency 9.87/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "raw_category": null,
        "materiality_reason": "Merger, acquisition or material business combination"
      }
    },
    {
      "id": "announcement:eaaac5ba475165f6a60984d98892a8608bff21e51cc78fb53582e48077261599",
      "ticker": "TITAN",
      "company_name": "Titan Company Limited",
      "kind": "filing",
      "category": "M&A",
      "headline": "Acquisition",
      "summary": "Acquisition",
      "priority": "high",
      "occurred_at": "2026-10-28T08:19:00Z",
      "citations": [
        {
          "document": "106831940",
          "locator": "2026-10-28T08:19:00Z",
          "quote": "Acquisition"
        }
      ],
      "materiality_score": 8.0,
      "source_reference": "106831940",
      "attachment_url": "https://nsearchives.nseindia.com/corporate/TITAN_28102026134838_SEIntimation_-_Canada_Incorporation.pdf",
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:52:28Z",
      "demo_mode": false,
      "rank_score": 152.29,
      "rank_reasons": [
        "Source materiality 8/10",
        "Category significance 9/9",
        "Company is marked in the portfolio",
        "Recency 9.29/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "raw_category": null,
        "materiality_reason": "Merger, acquisition or material business combination"
      }
    },
    {
      "id": "announcement:1cd6dbbd4304c8200e22f20c160605c9f673f4013a1fce5619298277dde039ec",
      "ticker": "SUZLON",
      "company_name": "Suzlon Energy Limited",
      "kind": "filing",
      "category": "credit_rating",
      "headline": "Credit Rating",
      "summary": "Credit Rating",
      "priority": "high",
      "occurred_at": "2026-10-30T12:52:36Z",
      "citations": [
        {
          "document": "106837091",
          "locator": "2026-10-30T12:52:36Z",
          "quote": "Credit Rating"
        }
      ],
      "materiality_score": 5.0,
      "source_reference": "106837091",
      "attachment_url": "https://nsearchives.nseindia.com/corporate/SUZLON1_30102026182203_Suzlon30102026.pdf",
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:52:23Z",
      "demo_mode": false,
      "rank_score": 112.53,
      "rank_reasons": [
        "Source materiality 5/10",
        "Category significance 7/9",
        "Company is marked in the portfolio",
        "Recency 9.53/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "raw_category": null,
        "materiality_reason": "Credit rating action; direction not stated",
        "duplicate_sources": [
          "106837091",
          "106831411"
        ],
        "duplicate_count": 2
      }
    },
    {
      "id": "announcement:1313d23d63d6f9e5fa148e391eb38361bf1ba3e98b0feab15ed734e89d911e5a",
      "ticker": "SUNPHARMA",
      "company_name": "Sun Pharmaceutical Industries Limited",
      "kind": "filing",
      "category": "insider_trading",
      "headline": "Rumour Verification - Regulation 30(11)",
      "summary": "Insider or designated-person trading disclosure",
      "priority": "medium",
      "occurred_at": "2026-11-02T15:28:22Z",
      "citations": [
        {
          "document": "106840669",
          "locator": "2026-11-02T15:28:22Z",
          "quote": "Rumour Verification - Regulation 30(11)"
        }
      ],
      "materiality_score": 4.0,
      "source_reference": "106840669",
      "attachment_url": "https://nsearchives.nseindia.com/corporate/SUNSEC_02112026205719_Reply_to_SEs_-_Rumour_Verification02112026.pdf",
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:52:20Z",
      "demo_mode": false,
      "rank_score": 92.88,
      "rank_reasons": [
        "Source materiality 4/10",
        "Category significance 5/9",
        "Company is marked in the portfolio",
        "Recency 9.88/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "raw_category": null,
        "materiality_reason": "Insider or designated-person trading disclosure"
      }
    },
    {
      "id": "announcement:3c9df33e6ccd1c2bba4205188f9db446f9acfcbfccd9e805e68fc714bdb9f9a7",
      "ticker": "SUZLON",
      "company_name": "Suzlon Energy Limited",
      "kind": "filing",
      "category": "insider_trading",
      "headline": "Rumour Verification - Regulation 30(11)",
      "summary": "Insider or designated-person trading disclosure",
      "priority": "medium",
      "occurred_at": "2026-10-30T08:58:30Z",
      "citations": [
        {
          "document": "106836294",
          "locator": "2026-10-30T08:58:30Z",
          "quote": "Rumour Verification - Regulation 30(11)"
        }
      ],
      "materiality_score": 4.0,
      "source_reference": "106836294",
      "attachment_url": "https://nsearchives.nseindia.com/corporate/SUZLON1_30102026142755_Suzlon30102026.pdf",
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:52:23Z",
      "demo_mode": false,
      "rank_score": 92.51,
      "rank_reasons": [
        "Source materiality 4/10",
        "Category significance 5/9",
        "Company is marked in the portfolio",
        "Recency 9.51/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "raw_category": null,
        "materiality_reason": "Insider or designated-person trading disclosure",
        "duplicate_sources": [
          "106836294",
          "106815376"
        ],
        "duplicate_count": 3
      }
    },
    {
      "id": "announcement:06699ded4bb5c6c73782d9bfcf6e461c9285c82362e8670dec9dbb53c9e5a2ff",
      "ticker": "SBIN",
      "company_name": "State Bank of India",
      "kind": "filing",
      "category": "investor_meetings",
      "headline": "Analysts/Institutional Investor Meet/Con. Call Updates",
      "summary": "Investor or analyst meeting notice",
      "priority": "low",
      "occurred_at": "2026-11-03T15:00:22Z",
      "citations": [
        {
          "document": "106842909",
          "locator": "2026-11-03T15:00:22Z",
          "quote": "Analysts/Institutional Investor Meet/Con. Call Updates"
        }
      ],
      "materiality_score": 2.0,
      "source_reference": "106842909",
      "attachment_url": "https://nsearchives.nseindia.com/corporate/SBIN_03112026202912_BSE_NSE_Post_Anlyst_recording_03112026.pdf",
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-03T17:06:53Z",
      "demo_mode": false,
      "rank_score": 62.99,
      "rank_reasons": [
        "Source materiality 2/10",
        "Category significance 3/9",
        "Company is marked in the portfolio",
        "Recency 9.99/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "raw_category": null,
        "materiality_reason": "Investor or analyst meeting notice",
        "duplicate_sources": [
          "106842909",
          "106835011"
        ],
        "duplicate_count": 3
      }
    },
    {
      "id": "announcement:97824ada0035c4483ece82d21e24ff8ab3c5197af68a8fb910d7dd7bb772e0ae",
      "ticker": "SBIN",
      "company_name": "State Bank of India",
      "kind": "filing",
      "category": "investor_meetings",
      "headline": "Investor Presentation",
      "summary": "Investor or analyst meeting notice",
      "priority": "low",
      "occurred_at": "2026-11-03T08:29:35Z",
      "citations": [
        {
          "document": "106841606",
          "locator": "2026-11-03T08:29:35Z",
          "quote": "Investor Presentation"
        }
      ],
      "materiality_score": 2.0,
      "source_reference": "106841606",
      "attachment_url": "https://nsearchives.nseindia.com/corporate/SBIN_03112026135925_Presentation.pdf",
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-03T17:06:53Z",
      "demo_mode": false,
      "rank_score": 62.96,
      "rank_reasons": [
        "Source materiality 2/10",
        "Category significance 3/9",
        "Company is marked in the portfolio",
        "Recency 9.96/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "raw_category": null,
        "materiality_reason": "Investor or analyst meeting notice"
      }
    },
    {
      "id": "announcement:aec1fa45d96cdab4ca4df1a47cea6bec54606b5cda69f709ae1535f6e16d7a85",
      "ticker": "DIXON",
      "company_name": "Dixon Technologies (India) Limited",
      "kind": "filing",
      "category": "investor_meetings",
      "headline": "Analysts/Institutional Investor Meet/Con. Call Updates",
      "summary": "Investor or analyst meeting notice",
      "priority": "low",
      "occurred_at": "2026-11-03T05:54:09Z",
      "citations": [
        {
          "document": "106841276",
          "locator": "2026-11-03T05:54:09Z",
          "quote": "Analysts/Institutional Investor Meet/Con. Call Updates"
        }
      ],
      "materiality_score": 2.0,
      "source_reference": "106841276",
      "attachment_url": "https://nsearchives.nseindia.com/corporate/DIXON_03112026112356_InvestorMeetOutcome031102026.pdf",
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-03T17:06:24Z",
      "demo_mode": false,
      "rank_score": 62.94,
      "rank_reasons": [
        "Source materiality 2/10",
        "Category significance 3/9",
        "Company is marked in the portfolio",
        "Recency 9.94/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "raw_category": null,
        "materiality_reason": "Investor or analyst meeting notice",
        "duplicate_sources": [
          "106841276",
          "106837485"
        ],
        "duplicate_count": 4
      }
    },
    {
      "id": "announcement:67c6c62244e98b582fac6022fc4055a26f7ce95f04b570f6944cf8f3b2abfdc8",
      "ticker": "MARUTI",
      "company_name": "Maruti Suzuki India Limited",
      "kind": "filing",
      "category": "investor_meetings",
      "headline": "Analysts/Institutional Investor Meet/Con. Call Updates",
      "summary": "Investor or analyst meeting notice",
      "priority": "low",
      "occurred_at": "2026-11-02T15:38:18Z",
      "citations": [
        {
          "document": "106840686",
          "locator": "2026-11-02T15:38:18Z",
          "quote": "Analysts/Institutional Investor Meet/Con. Call Updates"
        }
      ],
      "materiality_score": 2.0,
      "source_reference": "106840686",
      "attachment_url": "https://nsearchives.nseindia.com/corporate/MARUTIASHISH_02112026210459_Transcript_27Oct026.pdf",
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:52:07Z",
      "demo_mode": false,
      "rank_score": 62.88,
      "rank_reasons": [
        "Source materiality 2/10",
        "Category significance 3/9",
        "Company is marked in the portfolio",
        "Recency 9.88/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "raw_category": null,
        "materiality_reason": "Investor or analyst meeting notice",
        "duplicate_sources": [
          "106840686",
          "106823400"
        ],
        "duplicate_count": 3
      }
    },
    {
      "id": "announcement:c34d3d911792c4dac9676fced1ed9c2518753e4b79f74a0fb774583cb05c87eb",
      "ticker": "LT",
      "company_name": "Larsen & Toubro Limited",
      "kind": "filing",
      "category": "investor_meetings",
      "headline": "Analysts/Institutional Investor Meet/Con. Call Updates",
      "summary": "Investor or analyst meeting notice",
      "priority": "low",
      "occurred_at": "2026-11-02T12:26:36Z",
      "citations": [
        {
          "document": "106840137",
          "locator": "2026-11-02T12:26:36Z",
          "quote": "Analysts/Institutional Investor Meet/Con. Call Updates"
        }
      ],
      "materiality_score": 2.0,
      "source_reference": "106840137",
      "attachment_url": "https://nsearchives.nseindia.com/corporate/PAM_02112026175603_TranscriptSep2026.pdf",
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:52:03Z",
      "demo_mode": false,
      "rank_score": 62.86,
      "rank_reasons": [
        "Source materiality 2/10",
        "Category significance 3/9",
        "Company is marked in the portfolio",
        "Recency 9.86/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "raw_category": null,
        "materiality_reason": "Investor or analyst meeting notice",
        "duplicate_sources": [
          "106840137",
          "106831153"
        ],
        "duplicate_count": 3
      }
    },
    {
      "id": "announcement:450069379991c52710efc4e507a67a1bd1869100521d6130fb95c779544d3071",
      "ticker": "RELIANCE",
      "company_name": "Reliance Industries Limited",
      "kind": "filing",
      "category": "investor_meetings",
      "headline": "Analysts/Institutional Investor Meet/Con. Call Updates",
      "summary": "Investor or analyst meeting notice",
      "priority": "low",
      "occurred_at": "2026-11-01T17:39:22Z",
      "citations": [
        {
          "document": "106838897",
          "locator": "2026-11-01T17:39:22Z",
          "quote": "Analysts/Institutional Investor Meet/Con. Call Updates"
        }
      ],
      "materiality_score": 2.0,
      "source_reference": "106838897",
      "attachment_url": "https://nsearchives.nseindia.com/corporate/kavinavora_01112026230907_SE_01112026.pdf",
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:51:10Z",
      "demo_mode": false,
      "rank_score": 62.78,
      "rank_reasons": [
        "Source materiality 2/10",
        "Category significance 3/9",
        "Company is marked in the portfolio",
        "Recency 9.78/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "raw_category": null,
        "materiality_reason": "Investor or analyst meeting notice",
        "duplicate_sources": [
          "106838897",
          "106838338"
        ],
        "duplicate_count": 3
      }
    },
    {
      "id": "announcement:de5da24fea540022b3a8aacf78403269f39efc0f065e39fd3a5aab91c616909e",
      "ticker": "SUNPHARMA",
      "company_name": "Sun Pharmaceutical Industries Limited",
      "kind": "filing",
      "category": "investor_meetings",
      "headline": "Analysts/Institutional Investor Meet/Con. Call Updates",
      "summary": "Investor or analyst meeting notice",
      "priority": "low",
      "occurred_at": "2026-10-30T14:43:58Z",
      "citations": [
        {
          "document": "106837454",
          "locator": "2026-10-30T14:43:58Z",
          "quote": "Analysts/Institutional Investor Meet/Con. Call Updates"
        }
      ],
      "materiality_score": 2.0,
      "source_reference": "106837454",
      "attachment_url": "https://nsearchives.nseindia.com/corporate/SUNPHARMA456_30102026201207_IntimationSE20261030_Q2FY27_Call_Recording_Signed.pdf",
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:52:20Z",
      "demo_mode": false,
      "rank_score": 62.54,
      "rank_reasons": [
        "Source materiality 2/10",
        "Category significance 3/9",
        "Company is marked in the portfolio",
        "Recency 9.54/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "raw_category": null,
        "materiality_reason": "Investor or analyst meeting notice",
        "duplicate_sources": [
          "106837454",
          "106819024"
        ],
        "duplicate_count": 2
      }
    },
    {
      "id": "announcement:0b5d83801f81829c97c0d7f002a4996baab0928383668402c399589fd9e8dee3",
      "ticker": "RELIANCE",
      "company_name": "Reliance Industries Limited",
      "kind": "filing",
      "category": "investor_meetings",
      "headline": "Investor Presentation",
      "summary": "Investor or analyst meeting notice",
      "priority": "low",
      "occurred_at": "2026-10-30T14:17:12Z",
      "citations": [
        {
          "document": "106837413",
          "locator": "2026-10-30T14:17:12Z",
          "quote": "Investor Presentation"
        }
      ],
      "materiality_score": 2.0,
      "source_reference": "106837413",
      "attachment_url": "https://nsearchives.nseindia.com/corporate/kavinavora_30102026194557_SE_30102026_IP.pdf",
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:51:10Z",
      "demo_mode": false,
      "rank_score": 62.54,
      "rank_reasons": [
        "Source materiality 2/10",
        "Category significance 3/9",
        "Company is marked in the portfolio",
        "Recency 9.54/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "raw_category": null,
        "materiality_reason": "Investor or analyst meeting notice"
      }
    },
    {
      "id": "announcement:561bad92f45468db3678ebfea5ac2f91116675d54bdf53378f66694150cec6dd",
      "ticker": "HINDUNILVR",
      "company_name": "Hindustan Unilever Limited",
      "kind": "filing",
      "category": "investor_meetings",
      "headline": "Analysts/Institutional Investor Meet/Con. Call Updates",
      "summary": "Investor or analyst meeting notice",
      "priority": "low",
      "occurred_at": "2026-10-30T12:29:22Z",
      "citations": [
        {
          "document": "106837000",
          "locator": "2026-10-30T12:29:22Z",
          "quote": "Analysts/Institutional Investor Meet/Con. Call Updates"
        }
      ],
      "materiality_score": 2.0,
      "source_reference": "106837000",
      "attachment_url": "https://nsearchives.nseindia.com/corporate/HINDUNILVR_30102026175145_SEIntimationUnileverCapitalMarketsDay2026signed.pdf",
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:51:52Z",
      "demo_mode": false,
      "rank_score": 62.53,
      "rank_reasons": [
        "Source materiality 2/10",
        "Category significance 3/9",
        "Company is marked in the portfolio",
        "Recency 9.53/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "raw_category": null,
        "materiality_reason": "Investor or analyst meeting notice",
        "duplicate_sources": [
          "106837000",
          "106833120"
        ],
        "duplicate_count": 3
      }
    },
    {
      "id": "announcement:ed2d9790cae8d4edf5c57945d819a566fed9f46783655494424d9e39a6e10793",
      "ticker": "DIXON",
      "company_name": "Dixon Technologies (India) Limited",
      "kind": "filing",
      "category": "investor_meetings",
      "headline": "Investor Presentation",
      "summary": "Investor or analyst meeting notice",
      "priority": "low",
      "occurred_at": "2026-10-30T10:49:57Z",
      "citations": [
        {
          "document": "106836561",
          "locator": "2026-10-30T10:49:57Z",
          "quote": "Investor Presentation"
        }
      ],
      "materiality_score": 2.0,
      "source_reference": "106836561",
      "attachment_url": "https://nsearchives.nseindia.com/corporate/DIXON_30102026161836_OutcomewithPPT30102026.pdf",
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:51:47Z",
      "demo_mode": false,
      "rank_score": 62.52,
      "rank_reasons": [
        "Source materiality 2/10",
        "Category significance 3/9",
        "Company is marked in the portfolio",
        "Recency 9.52/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "raw_category": null,
        "materiality_reason": "Investor or analyst meeting notice"
      }
    },
    {
      "id": "announcement:299e87c7d3dfd5e64f3aeb488d5c97b9b56d58ad83054ff0759340e3d9da1fbf",
      "ticker": "SUZLON",
      "company_name": "Suzlon Energy Limited",
      "kind": "filing",
      "category": "investor_meetings",
      "headline": "Analysts/Institutional Investor Meet/Con. Call Updates",
      "summary": "Investor or analyst meeting notice",
      "priority": "low",
      "occurred_at": "2026-10-29T15:06:10Z",
      "citations": [
        {
          "document": "106835327",
          "locator": "2026-10-29T15:06:10Z",
          "quote": "Analysts/Institutional Investor Meet/Con. Call Updates"
        }
      ],
      "materiality_score": 2.0,
      "source_reference": "106835327",
      "attachment_url": "https://nsearchives.nseindia.com/corporate/SUZLON1_29102026203518_Suzlon29102026.pdf",
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:52:23Z",
      "demo_mode": false,
      "rank_score": 62.43,
      "rank_reasons": [
        "Source materiality 2/10",
        "Category significance 3/9",
        "Company is marked in the portfolio",
        "Recency 9.43/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "raw_category": null,
        "materiality_reason": "Investor or analyst meeting notice",
        "duplicate_sources": [
          "106835327",
          "106828917"
        ],
        "duplicate_count": 2
      }
    },
    {
      "id": "announcement:3d350944c6aeeae8f3612196d00efdcf1d864975f50f56386935df5be18cb13c",
      "ticker": "TRENT",
      "company_name": "Trent Limited",
      "kind": "filing",
      "category": "investor_meetings",
      "headline": "Investor Presentation",
      "summary": "Investor or analyst meeting notice",
      "priority": "low",
      "occurred_at": "2026-10-29T10:47:38Z",
      "citations": [
        {
          "document": "106834446",
          "locator": "2026-10-29T10:47:38Z",
          "quote": "Investor Presentation"
        }
      ],
      "materiality_score": 2.0,
      "source_reference": "106834446",
      "attachment_url": "https://nsearchives.nseindia.com/corporate/TRENT_29102026161637_InvestorPresentationQ2FY27.pdf",
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:52:30Z",
      "demo_mode": false,
      "rank_score": 62.41,
      "rank_reasons": [
        "Source materiality 2/10",
        "Category significance 3/9",
        "Company is marked in the portfolio",
        "Recency 9.41/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "raw_category": null,
        "materiality_reason": "Investor or analyst meeting notice"
      }
    },
    {
      "id": "announcement:890308d129937b6083e59962954f7d1bbb5a661b91755334f259636055b76590",
      "ticker": "HINDUNILVR",
      "company_name": "Hindustan Unilever Limited",
      "kind": "filing",
      "category": "investor_meetings",
      "headline": "Investor Presentation",
      "summary": "Investor or analyst meeting notice",
      "priority": "low",
      "occurred_at": "2026-10-28T04:13:04Z",
      "citations": [
        {
          "document": "106831490",
          "locator": "2026-10-28T04:13:04Z",
          "quote": "Investor Presentation"
        }
      ],
      "materiality_score": 2.0,
      "source_reference": "106831490",
      "attachment_url": "https://nsearchives.nseindia.com/corporate/HINDUNILVR_28102026094216_SEintimationIPSigned.pdf",
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:51:52Z",
      "demo_mode": false,
      "rank_score": 62.27,
      "rank_reasons": [
        "Source materiality 2/10",
        "Category significance 3/9",
        "Company is marked in the portfolio",
        "Recency 9.27/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "raw_category": null,
        "materiality_reason": "Investor or analyst meeting notice"
      }
    },
    {
      "id": "announcement:a6a4105f0d55e94be19923144d51c4499018462f7e55fa2a41478bcc4f7e8abe",
      "ticker": "SBIN",
      "company_name": "State Bank of India",
      "kind": "filing",
      "category": "press_release",
      "headline": "Press Release",
      "summary": "General press or media release; conservative default",
      "priority": "low",
      "occurred_at": "2026-11-03T08:29:35Z",
      "citations": [
        {
          "document": "106841605",
          "locator": "2026-11-03T08:29:35Z",
          "quote": "Press Release"
        }
      ],
      "materiality_score": 2.0,
      "source_reference": "106841605",
      "attachment_url": "https://nsearchives.nseindia.com/corporate/SBIN_03112026135813_PressRelease.pdf",
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-03T17:06:53Z",
      "demo_mode": false,
      "rank_score": 57.96,
      "rank_reasons": [
        "Source materiality 2/10",
        "Category significance 2/9",
        "Company is marked in the portfolio",
        "Recency 9.96/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "raw_category": null,
        "materiality_reason": "General press or media release; conservative default"
      }
    },
    {
      "id": "anomaly:fc9b53dc1fbb860bfbc64cbe",
      "ticker": "SBIN",
      "company_name": "State Bank of India",
      "kind": "anomaly",
      "category": "volume_anomaly",
      "headline": "Trading anomaly detected",
      "summary": "Volume 3.1x its 20-day average",
      "priority": "medium",
      "occurred_at": "2026-11-03T00:00:00Z",
      "citations": [],
      "materiality_score": null,
      "source_reference": "prices:2026-11-03",
      "attachment_url": null,
      "data_source": "yfinance",
      "source": "yfinance",
      "fetched_at": "2026-11-03T00:00:00Z",
      "demo_mode": false,
      "rank_score": 57.92,
      "rank_reasons": [
        "Category significance 6/9",
        "Company is marked in the portfolio",
        "Recency 9.92/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "anomalies": [
          {
            "type": "volume_spike",
            "observed_value": 3.0791365974548848,
            "threshold_value": 2.0,
            "unit": "multiple"
          }
        ]
      }
    },
    {
      "id": "anomaly:f580370cc10d346ac2c49d0a",
      "ticker": "HDFCBANK",
      "company_name": "HDFC Bank Limited",
      "kind": "anomaly",
      "category": "price_anomaly",
      "headline": "Trading anomaly detected",
      "summary": "price +3.6%",
      "priority": "medium",
      "occurred_at": "2026-11-03T00:00:00Z",
      "citations": [],
      "materiality_score": null,
      "source_reference": "prices:2026-11-03",
      "attachment_url": null,
      "data_source": "yfinance",
      "source": "yfinance",
      "fetched_at": "2026-11-03T00:00:00Z",
      "demo_mode": false,
      "rank_score": 57.92,
      "rank_reasons": [
        "Category significance 6/9",
        "Company is marked in the portfolio",
        "Recency 9.92/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "anomalies": [
          {
            "type": "price_move",
            "observed_value": 3.6428571428571477,
            "threshold_value": 3.0,
            "unit": "percent"
          }
        ]
      }
    },
    {
      "id": "anomaly:d2efd7433b847b4117a670af",
      "ticker": "HINDUNILVR",
      "company_name": "Hindustan Unilever Limited",
      "kind": "anomaly",
      "category": "price_anomaly",
      "headline": "Trading anomaly detected",
      "summary": "price +3.4%",
      "priority": "medium",
      "occurred_at": "2026-11-03T00:00:00Z",
      "citations": [],
      "materiality_score": null,
      "source_reference": "prices:2026-11-03",
      "attachment_url": null,
      "data_source": "yfinance",
      "source": "yfinance",
      "fetched_at": "2026-11-03T00:00:00Z",
      "demo_mode": false,
      "rank_score": 57.92,
      "rank_reasons": [
        "Category significance 6/9",
        "Company is marked in the portfolio",
        "Recency 9.92/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "anomalies": [
          {
            "type": "price_move",
            "observed_value": 3.3977768709334333,
            "threshold_value": 3.0,
            "unit": "percent"
          }
        ]
      }
    },
    {
      "id": "anomaly:3be8b98a0fc1367a27348df3",
      "ticker": "RELIANCE",
      "company_name": "Reliance Industries Limited",
      "kind": "anomaly",
      "category": "volume_anomaly",
      "headline": "Trading anomaly detected",
      "summary": "Volume 2.3x its 20-day average",
      "priority": "medium",
      "occurred_at": "2026-11-03T00:00:00Z",
      "citations": [],
      "materiality_score": null,
      "source_reference": "prices:2026-11-03",
      "attachment_url": null,
      "data_source": "yfinance",
      "source": "yfinance",
      "fetched_at": "2026-11-03T00:00:00Z",
      "demo_mode": false,
      "rank_score": 57.92,
      "rank_reasons": [
        "Category significance 6/9",
        "Company is marked in the portfolio",
        "Recency 9.92/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "anomalies": [
          {
            "type": "volume_spike",
            "observed_value": 2.26652220228089,
            "threshold_value": 2.0,
            "unit": "multiple"
          }
        ]
      }
    },
    {
      "id": "announcement:2455171eed6a4a0e9ad7f509b435f38291c13c6c94c83a2b4fc790bb86cab32b",
      "ticker": "MARUTI",
      "company_name": "Maruti Suzuki India Limited",
      "kind": "filing",
      "category": "press_release",
      "headline": "Press Release",
      "summary": "General press or media release; conservative default",
      "priority": "low",
      "occurred_at": "2026-11-01T08:15:06Z",
      "citations": [
        {
          "document": "106838779",
          "locator": "2026-11-01T08:15:06Z",
          "quote": "Press Release"
        }
      ],
      "materiality_score": 2.0,
      "source_reference": "106838779",
      "attachment_url": "https://nsearchives.nseindia.com/corporate/MARUTIASHISH_01112026133641_StxIntimation_Sales_Oct2026.pdf",
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:52:07Z",
      "demo_mode": false,
      "rank_score": 57.73,
      "rank_reasons": [
        "Source materiality 2/10",
        "Category significance 2/9",
        "Company is marked in the portfolio",
        "Recency 9.73/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "raw_category": null,
        "materiality_reason": "General press or media release; conservative default",
        "duplicate_sources": [
          "106838779",
          "106833712"
        ],
        "duplicate_count": 4
      }
    },
    {
      "id": "announcement:2848649f232ff098cabd8bc997c009f5b046bc08ffd0710a9e4510b592c2a9a3",
      "ticker": "RELIANCE",
      "company_name": "Reliance Industries Limited",
      "kind": "filing",
      "category": "press_release",
      "headline": "Press Release",
      "summary": "General press or media release; conservative default",
      "priority": "low",
      "occurred_at": "2026-10-30T14:13:24Z",
      "citations": [
        {
          "document": "106837406",
          "locator": "2026-10-30T14:13:24Z",
          "quote": "Press Release"
        }
      ],
      "materiality_score": 2.0,
      "source_reference": "106837406",
      "attachment_url": "https://nsearchives.nseindia.com/corporate/kavinavora_30102026194315_SE_30102026_MR.pdf",
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:51:10Z",
      "demo_mode": false,
      "rank_score": 57.54,
      "rank_reasons": [
        "Source materiality 2/10",
        "Category significance 2/9",
        "Company is marked in the portfolio",
        "Recency 9.54/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "raw_category": null,
        "materiality_reason": "General press or media release; conservative default"
      }
    },
    {
      "id": "announcement:b638d75d4f6a94face27816f58660a39376aee57611eaea6ed59cec274a26ff4",
      "ticker": "SUNPHARMA",
      "company_name": "Sun Pharmaceutical Industries Limited",
      "kind": "filing",
      "category": "press_release",
      "headline": "Press Release",
      "summary": "General press or media release; conservative default",
      "priority": "low",
      "occurred_at": "2026-10-30T02:35:47Z",
      "citations": [
        {
          "document": "106835654",
          "locator": "2026-10-30T02:35:47Z",
          "quote": "Press Release"
        }
      ],
      "materiality_score": 2.0,
      "source_reference": "106835654",
      "attachment_url": "https://nsearchives.nseindia.com/corporate/SUNSEC_30102026080437_SE_Intimation_of_Press_Release_ILUMYA_PsA_Approval.pdf",
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:52:20Z",
      "demo_mode": false,
      "rank_score": 57.48,
      "rank_reasons": [
        "Source materiality 2/10",
        "Category significance 2/9",
        "Company is marked in the portfolio",
        "Recency 9.48/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "raw_category": null,
        "materiality_reason": "General press or media release; conservative default",
        "duplicate_sources": [
          "106835654",
          "106826784"
        ],
        "duplicate_count": 4
      }
    },
    {
      "id": "announcement:86814543de2caab9cee25862549a8f60ab4c9ffb61dd8cdeda549700d8e25486",
      "ticker": "TRENT",
      "company_name": "Trent Limited",
      "kind": "filing",
      "category": "press_release",
      "headline": "Press Release",
      "summary": "General press or media release; conservative default",
      "priority": "low",
      "occurred_at": "2026-10-29T10:51:37Z",
      "citations": [
        {
          "document": "106834466",
          "locator": "2026-10-29T10:51:37Z",
          "quote": "Press Release"
        }
      ],
      "materiality_score": 2.0,
      "source_reference": "106834466",
      "attachment_url": "https://nsearchives.nseindia.com/corporate/TRENT_29102026162053_PressReleaseOct2026.pdf",
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:52:30Z",
      "demo_mode": false,
      "rank_score": 57.41,
      "rank_reasons": [
        "Source materiality 2/10",
        "Category significance 2/9",
        "Company is marked in the portfolio",
        "Recency 9.41/10",
        "Source reference available",
        "Supporting details available"
      ],
      "collapsed_count": 1,
      "supporting_details": {
        "raw_category": null,
        "materiality_reason": "General press or media release; conservative default",
        "duplicate_sources": [
          "106834466",
          "106807380"
        ],
        "duplicate_count": 2
      }
    },
    {
      "id": "routine:4d08f42f4178eafd10d77977",
      "ticker": "TCS",
      "company_name": "Tata Consultancy Services Limited",
      "kind": "filing",
      "category": "unclassified",
      "headline": "5 routine unclassified disclosures",
      "summary": "5 lower-materiality disclosures of this category are grouped here; expand for the individual filings.",
      "priority": "low",
      "occurred_at": "2026-11-03T13:22:12Z",
      "citations": [
        {
          "document": "106842587",
          "locator": "2026-11-03T13:22:12Z",
          "quote": "Copy of Newspaper Publication"
        },
        {
          "document": "106821698",
          "locator": "2026-10-19T06:00:07Z",
          "quote": "Updates"
        },
        {
          "document": "106818480",
          "locator": "2026-10-15T08:00:23Z",
          "quote": "General Updates"
        },
        {
          "document": "106811188",
          "locator": "2026-10-08T10:12:03Z",
          "quote": "Dividend"
        },
        {
          "document": "106811186",
          "locator": "2026-10-08T10:10:12Z",
          "quote": "Outcome of Board Meeting"
        }
      ],
      "materiality_score": 1.0,
      "source_reference": null,
      "attachment_url": null,
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-03T17:07:01Z",
      "demo_mode": false,
      "rank_score": 40.98,
      "rank_reasons": [
        "Source materiality 1/10",
        "Category significance 1/9",
        "Company is marked in the portfolio",
        "Recency 9.98/10",
        "Supporting details available"
      ],
      "collapsed_count": 5,
      "supporting_details": {
        "grouped_events": [
          {
            "id": "announcement:dc90d6c0d5847c45f9c6ba19e6565ee8733b07b8a58e2370e9e4dae393cde890",
            "headline": "Copy of Newspaper Publication",
            "occurred_at": "2026-11-03T13:22:12Z",
            "source_reference": "106842587",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/TCS_CORPCS_03112026185113_SEInt3112026_signed.pdf"
          },
          {
            "id": "announcement:fb8b24c80d46267f92c23546c8cfc268aa7fd60c1b0ccd00ed30a3cddf8bdd4c",
            "headline": "Updates",
            "occurred_at": "2026-10-19T06:00:07Z",
            "source_reference": "106821698",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/TCS_CORPCS_19102026112258_PR_19Oct26_signed.pdf"
          },
          {
            "id": "announcement:0bd3d23b541d1327346d9c495facfc48a6fb797ae41fec6a2dab1e8f7a0925bc",
            "headline": "General Updates",
            "occurred_at": "2026-10-15T08:00:23Z",
            "source_reference": "106818480",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/TCS_CORPCS_15102026133009_SEInt15102026.pdf"
          },
          {
            "id": "announcement:d14fcac4e33e4a7b17134897fc004852343b0646d47b73e4d6c96dfc3f2e3590",
            "headline": "Dividend",
            "occurred_at": "2026-10-08T10:12:03Z",
            "source_reference": "106811188",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/TCS_CORPCS_08102026154152_Post_BM_SE_Letter_fin.pdf"
          },
          {
            "id": "announcement:8300ed1e4c7b3e4630a06dabdd2e92982fb10083e82b222dedf9d5c5f9378073",
            "headline": "Outcome of Board Meeting",
            "occurred_at": "2026-10-08T10:10:12Z",
            "source_reference": "106811186",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/TCS_CORPCS_08102026153124_Post_BM_SE_Letter_fin.pdf"
          }
        ]
      }
    },
    {
      "id": "routine:8d641dbd9ea956f4e16c29c5",
      "ticker": "DIXON",
      "company_name": "Dixon Technologies (India) Limited",
      "kind": "filing",
      "category": "unclassified",
      "headline": "7 routine unclassified disclosures",
      "summary": "7 lower-materiality disclosures of this category are grouped here; expand for the individual filings.",
      "priority": "low",
      "occurred_at": "2026-11-03T12:00:12Z",
      "citations": [
        {
          "document": "106842234",
          "locator": "2026-11-03T12:00:12Z",
          "quote": "Updates"
        },
        {
          "document": "106838529",
          "locator": "2026-10-31T14:02:44Z",
          "quote": "Copy of Newspaper Publication"
        },
        {
          "document": "106836531",
          "locator": "2026-10-30T10:40:12Z",
          "quote": "Change in Management"
        },
        {
          "document": "106836523",
          "locator": "2026-10-30T10:37:23Z",
          "quote": "Outcome of Board Meeting"
        },
        {
          "document": "106817628",
          "locator": "2026-10-14T12:55:23Z",
          "quote": "General Updates"
        },
        {
          "document": "106812913",
          "locator": "2026-10-09T12:53:50Z",
          "quote": "Certificate under SEBI (Depositories and Participants) Regulations, 2018"
        },
        {
          "document": "106809698",
          "locator": "2026-10-07T09:31:51Z",
          "quote": "Agreements"
        }
      ],
      "materiality_score": 1.0,
      "source_reference": null,
      "attachment_url": null,
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-03T17:06:24Z",
      "demo_mode": false,
      "rank_score": 40.97,
      "rank_reasons": [
        "Source materiality 1/10",
        "Category significance 1/9",
        "Company is marked in the portfolio",
        "Recency 9.97/10",
        "Supporting details available"
      ],
      "collapsed_count": 7,
      "supporting_details": {
        "grouped_events": [
          {
            "id": "announcement:4b200d5b9d340d9834bdaa598e4f1ea5df4d6e15fd8cfddeda4359ff7b9ff027",
            "headline": "Updates",
            "occurred_at": "2026-11-03T12:00:12Z",
            "source_reference": "106842234",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/DIXON_03112026172946_Regulation30DisclosureRTAAddress.pdf"
          },
          {
            "id": "announcement:a624fb225b5fbc561d0936c82080f5823735e7a8a8c3bf8054af0c2d8d0a0968",
            "headline": "Copy of Newspaper Publication",
            "occurred_at": "2026-10-31T14:02:44Z",
            "source_reference": "106838529",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/DIXON_31102026192630_NewspaperAdvertisement31101026.pdf"
          },
          {
            "id": "announcement:810c7bad8e3bd18f141e52512c2acc78282050de44d5cc09e8c6f11ddf5c7bad",
            "headline": "Change in Management",
            "occurred_at": "2026-10-30T10:40:12Z",
            "source_reference": "106836531",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/DIXON_30102026160939_Outcome30102026.pdf"
          },
          {
            "id": "announcement:54fc761e6b0be6b9c95687d8f70c096770cf32f9f5367eddb438bff1e06fe69f",
            "headline": "Outcome of Board Meeting",
            "occurred_at": "2026-10-30T10:37:23Z",
            "source_reference": "106836523",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/DIXON_30102026160547_Outcome30102026.pdf"
          },
          {
            "id": "announcement:42c265c5b0426030ffdbf1e9e7ccd72a5e642581fa10be69e5da88630c158158",
            "headline": "General Updates",
            "occurred_at": "2026-10-14T12:55:23Z",
            "source_reference": "106817628",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/DIXON_14102026182232_ESGRatingDisclousureCrisil14102026.pdf"
          },
          {
            "id": "announcement:aa004b5d9d683b1b761a642c80d6782dc4567dcaa92c0e2a25de5907bd9c308f",
            "headline": "Certificate under SEBI (Depositories and Participants) Regulations, 2018",
            "occurred_at": "2026-10-09T12:53:50Z",
            "source_reference": "106812913",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/DIXON_09102026182235_Reg74_5_Disclosure09102026.pdf"
          },
          {
            "id": "announcement:dfc57b4eb4ebb8f51a000d56601fdee6d0a82fe98ee37a062a18a88a294418d4",
            "headline": "Agreements",
            "occurred_at": "2026-10-07T09:31:51Z",
            "source_reference": "106809698",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/DIXON_07102026150006_Regulation30_DisclosureGemtek07102026.pdf"
          }
        ]
      }
    },
    {
      "id": "routine:4ed801dddb456c61ca31b3a2",
      "ticker": "M&M",
      "company_name": "Mahindra & Mahindra Limited",
      "kind": "filing",
      "category": "unclassified",
      "headline": "5 routine unclassified disclosures",
      "summary": "5 lower-materiality disclosures of this category are grouped here; expand for the individual filings.",
      "priority": "low",
      "occurred_at": "2026-11-03T10:37:13Z",
      "citations": [
        {
          "document": "106841911",
          "locator": "2026-11-03T10:37:13Z",
          "quote": "Updates"
        },
        {
          "document": "106838749",
          "locator": "2026-11-01T04:45:10Z",
          "quote": "Monthly Business Updates"
        },
        {
          "document": "106820992",
          "locator": "2026-10-17T07:08:10Z",
          "quote": "General Updates"
        },
        {
          "document": "106820100",
          "locator": "2026-10-16T09:52:12Z",
          "quote": "Copy of Newspaper Publication"
        },
        {
          "document": "106813278",
          "locator": "2026-10-09T17:50:18Z",
          "quote": "Sale or disposal"
        }
      ],
      "materiality_score": 1.0,
      "source_reference": null,
      "attachment_url": null,
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-03T17:06:40Z",
      "demo_mode": false,
      "rank_score": 40.97,
      "rank_reasons": [
        "Source materiality 1/10",
        "Category significance 1/9",
        "Company is marked in the portfolio",
        "Recency 9.97/10",
        "Supporting details available"
      ],
      "collapsed_count": 5,
      "supporting_details": {
        "grouped_events": [
          {
            "id": "announcement:ade4d110f8f568f765beaf1f775b78a2f8e922fe30c4c410bcca5d4308a7a8c1",
            "headline": "Updates",
            "occurred_at": "2026-11-03T10:37:13Z",
            "source_reference": "106841911",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/Deepak_03112026160659_SE_Intimation_Change_of_Kfintech_Corporate_Office.pdf"
          },
          {
            "id": "announcement:ebd386af19decd979c57d12e473b92b343500194520ff3ac2e5f826ea5eb2c17",
            "headline": "Monthly Business Updates",
            "occurred_at": "2026-11-01T04:45:10Z",
            "source_reference": "106838749",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/ferozebaria_01112026101454_SEIntimationNovember2026PR.pdf"
          },
          {
            "id": "announcement:be3034693e85aafbde09773dcfd1dd9c91b9b0db2b53438930967f6e7cdb34d5",
            "headline": "General Updates",
            "occurred_at": "2026-10-17T07:08:10Z",
            "source_reference": "106820992",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/AmitDodani_17102026123753_SE_Intimation_NDET_Dilution.pdf"
          },
          {
            "id": "announcement:5cb86c8153682035f28c3b0863267bde1410e312deab5312576c89448a77481a",
            "headline": "Copy of Newspaper Publication",
            "occurred_at": "2026-10-16T09:52:12Z",
            "source_reference": "106820100",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/Deepak_16102026152139_SE_INTIMATION_LOST_OF_SHARE_CERTIFICATE_2026_-_OCT_.pdf"
          },
          {
            "id": "announcement:5e723eb001a798f7d30c7d94802afd7260a783ff4575655cac14d6f418e683df",
            "headline": "Sale or disposal",
            "occurred_at": "2026-10-09T17:50:18Z",
            "source_reference": "106813278",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/AmitDodani_09102026232007_Novavayu_SE_Intimation_Investment_Agreement_Revised.pdf"
          }
        ]
      }
    },
    {
      "id": "routine:0412468cd0fb5b0cfa96cae5",
      "ticker": "SBIN",
      "company_name": "State Bank of India",
      "kind": "filing",
      "category": "unclassified",
      "headline": "5 routine unclassified disclosures",
      "summary": "5 lower-materiality disclosures of this category are grouped here; expand for the individual filings.",
      "priority": "low",
      "occurred_at": "2026-11-03T09:42:51Z",
      "citations": [
        {
          "document": "106841767",
          "locator": "2026-11-03T09:42:51Z",
          "quote": "Statement of deviation(s) or variation(s) under Reg. 32"
        },
        {
          "document": "106841577",
          "locator": "2026-11-03T08:17:53Z",
          "quote": "Outcome of Board Meeting"
        },
        {
          "document": "106822872",
          "locator": "2026-10-21T03:21:09Z",
          "quote": "General Updates"
        },
        {
          "document": "106812599",
          "locator": "2026-10-09T10:20:05Z",
          "quote": "Copy of Newspaper Publication"
        },
        {
          "document": "106811266",
          "locator": "2026-10-08T10:57:09Z",
          "quote": "Certificate under SEBI (Depositories and Participants) Regulations, 2018"
        }
      ],
      "materiality_score": 1.0,
      "source_reference": null,
      "attachment_url": null,
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-03T17:06:53Z",
      "demo_mode": false,
      "rank_score": 40.96,
      "rank_reasons": [
        "Source materiality 1/10",
        "Category significance 1/9",
        "Company is marked in the portfolio",
        "Recency 9.96/10",
        "Supporting details available"
      ],
      "collapsed_count": 5,
      "supporting_details": {
        "grouped_events": [
          {
            "id": "announcement:bb7749101ebf339cd921cf671c097eb8b39a637f8482fae3a00dc79af5f3f473",
            "headline": "Statement of deviation(s) or variation(s) under Reg. 32",
            "occurred_at": "2026-11-03T09:42:51Z",
            "source_reference": "106841767",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/SBIN_03112026151233_DeviationUtilisation.pdf"
          },
          {
            "id": "announcement:42c320142d553329d4f60fa54bda9fb177ef9736808f2ee1585d4630d4a94143",
            "headline": "Outcome of Board Meeting",
            "occurred_at": "2026-11-03T08:17:53Z",
            "source_reference": "106841577",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/SBIN_03112026134649_FR_DSC.pdf"
          },
          {
            "id": "announcement:673acc75f4c46e847249e5b0f5e300aa242abd8296137f86d3a76ca8b8e34389",
            "headline": "General Updates",
            "occurred_at": "2026-10-21T03:21:09Z",
            "source_reference": "106822872",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/SBIN_21102026084938_BSE_NSE_21102026.pdf"
          },
          {
            "id": "announcement:8b402f02776391a657cb6217fcad70c358dab38b01bff44a351d9e1803556d41",
            "headline": "Copy of Newspaper Publication",
            "occurred_at": "2026-10-09T10:20:05Z",
            "source_reference": "106812599",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/SBIN_09102026154949_NewsPaper09102026.pdf"
          },
          {
            "id": "announcement:db81345dcca3b1058c37831652a0027f94ec8f062ce152f0d3d960e99e43fca6",
            "headline": "Certificate under SEBI (Depositories and Participants) Regulations, 2018",
            "occurred_at": "2026-10-08T10:57:09Z",
            "source_reference": "106811266",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/SBIN_08102026162654_BSE_NSE_74_5__08102026.pdf"
          }
        ]
      }
    },
    {
      "id": "routine:0cd90a5d65198bdc75dbc4c8",
      "ticker": "BAJFINANCE",
      "company_name": "Bajaj Finance Limited",
      "kind": "filing",
      "category": "unclassified",
      "headline": "8 routine unclassified disclosures",
      "summary": "8 lower-materiality disclosures of this category are grouped here; expand for the individual filings.",
      "priority": "low",
      "occurred_at": "2026-11-02T14:01:06Z",
      "citations": [
        {
          "document": "106840525",
          "locator": "2026-11-02T14:01:06Z",
          "quote": "Shareholders meeting"
        },
        {
          "document": "106836343",
          "locator": "2026-10-30T09:23:37Z",
          "quote": "Allotment of Securities"
        },
        {
          "document": "106822209",
          "locator": "2026-10-19T12:27:20Z",
          "quote": "Change in Management"
        },
        {
          "document": "106822208",
          "locator": "2026-10-19T12:27:20Z",
          "quote": "Issue of Securities"
        },
        {
          "document": "106822125",
          "locator": "2026-10-19T11:50:38Z",
          "quote": "Outcome of Board Meeting"
        },
        {
          "document": "106813631",
          "locator": "2026-10-10T11:49:27Z",
          "quote": "Copy of Newspaper Publication"
        },
        {
          "document": "106810209",
          "locator": "2026-10-07T13:22:28Z",
          "quote": "Certificate under SEBI (Depositories and Participants) Regulations, 2018"
        },
        {
          "document": "106806160",
          "locator": "2026-10-03T05:32:00Z",
          "quote": "General Updates"
        }
      ],
      "materiality_score": 1.0,
      "source_reference": null,
      "attachment_url": null,
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:51:45Z",
      "demo_mode": false,
      "rank_score": 40.87,
      "rank_reasons": [
        "Source materiality 1/10",
        "Category significance 1/9",
        "Company is marked in the portfolio",
        "Recency 9.87/10",
        "Supporting details available"
      ],
      "collapsed_count": 8,
      "supporting_details": {
        "grouped_events": [
          {
            "id": "announcement:1ce37079794f028215f9be075de6c29d1953a38a7e44157d57849b6d0469e9df",
            "headline": "Shareholders meeting",
            "occurred_at": "2026-11-02T14:01:06Z",
            "source_reference": "106840525",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/BAJFINANCE_02112026193032_BFLEGMProceedings.pdf"
          },
          {
            "id": "announcement:dcccd0f2d436f08541ceca8f716e3cc4c35c36b4388abbabfa823b232d388c76",
            "headline": "Allotment of Securities",
            "occurred_at": "2026-10-30T09:23:37Z",
            "source_reference": "106836343",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/BAJFINANCE_30102026145301_REG30_Allotment_intimation.pdf"
          },
          {
            "id": "announcement:54227b7cd7f12398b9ed05a23b484b7dfdf4b873f10f4c5268473c6df079302d",
            "headline": "Change in Management",
            "occurred_at": "2026-10-19T12:27:20Z",
            "source_reference": "106822209",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/BAJFINANCE_19102026175648_Change_in_SMT_Prashant_Verma_CISO_signed.pdf"
          },
          {
            "id": "announcement:7e0c26533d2000cae741944eb3b93ddb22be11ee23e277e4eae2c92416ce4764",
            "headline": "Issue of Securities",
            "occurred_at": "2026-10-19T12:27:20Z",
            "source_reference": "106822208",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/BAJFINANCE_19102026175355_Issue_of_Securities_19102026.pdf"
          },
          {
            "id": "announcement:5a2eb89eb2bdd935e331209eeff53a1f67f9ceb1dece69d3ae824cf9b40c3141",
            "headline": "Outcome of Board Meeting",
            "occurred_at": "2026-10-19T11:50:38Z",
            "source_reference": "106822125",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/BAJFINANCE_19102026172017_BMOutcome_19102026.pdf"
          },
          {
            "id": "announcement:0af2460135052388df4d064b88db20ab11b540a4687ee26163212041b3ae867c",
            "headline": "Copy of Newspaper Publication",
            "occurred_at": "2026-10-10T11:49:27Z",
            "source_reference": "106813631",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/BAJFINANCE_10102026171855_SEIntimationnewspaperadvt_Sd.pdf"
          },
          {
            "id": "announcement:2bb5aa02e9ce017e979c4c6c7d86e6c33f8eae29b387ac70d08f08f37e30d7f8",
            "headline": "Certificate under SEBI (Depositories and Participants) Regulations, 2018",
            "occurred_at": "2026-10-07T13:22:28Z",
            "source_reference": "106810209",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/BAJFINANCE_07102026185211_74_5__sd.pdf"
          },
          {
            "id": "announcement:8717b5aaf38f0f49f021ed31bc081c8244eca42e38ad05d138fbbeb6b5e0f4be",
            "headline": "General Updates",
            "occurred_at": "2026-10-03T05:32:00Z",
            "source_reference": "106806160",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/BAJFINANCE_03102026110139_BFL_Pre-results_earning_intimation_Q2FY2027.pdf"
          }
        ]
      }
    },
    {
      "id": "routine:0cf116d83101603a70222b1c",
      "ticker": "SUNPHARMA",
      "company_name": "Sun Pharmaceutical Industries Limited",
      "kind": "filing",
      "category": "unclassified",
      "headline": "7 routine unclassified disclosures",
      "summary": "7 lower-materiality disclosures of this category are grouped here; expand for the individual filings.",
      "priority": "low",
      "occurred_at": "2026-11-02T08:48:39Z",
      "citations": [
        {
          "document": "106839459",
          "locator": "2026-11-02T08:48:39Z",
          "quote": "News Verification"
        },
        {
          "document": "106838574",
          "locator": "2026-10-31T14:44:24Z",
          "quote": "General Updates"
        },
        {
          "document": "106838334",
          "locator": "2026-10-31T12:02:02Z",
          "quote": "Copy of Newspaper Publication"
        },
        {
          "document": "106836275",
          "locator": "2026-10-30T08:45:10Z",
          "quote": "Outcome of Board Meeting"
        },
        {
          "document": "106828196",
          "locator": "2026-10-26T07:00:34Z",
          "quote": "Allotment of Securities"
        },
        {
          "document": "106817485",
          "locator": "2026-10-14T12:08:55Z",
          "quote": "Certificate under SEBI (Depositories and Participants) Regulations, 2018"
        },
        {
          "document": "106815017",
          "locator": "2026-10-12T14:35:00Z",
          "quote": "Resignation"
        }
      ],
      "materiality_score": 1.0,
      "source_reference": null,
      "attachment_url": null,
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:52:20Z",
      "demo_mode": false,
      "rank_score": 40.85,
      "rank_reasons": [
        "Source materiality 1/10",
        "Category significance 1/9",
        "Company is marked in the portfolio",
        "Recency 9.85/10",
        "Supporting details available"
      ],
      "collapsed_count": 7,
      "supporting_details": {
        "grouped_events": [
          {
            "id": "announcement:9a5ace5e03128f4542b0861fcf2be450cc1aa14622110921498941d901752d49",
            "headline": "News Verification",
            "occurred_at": "2026-11-02T08:48:39Z",
            "source_reference": "106839459",
            "attachment_url": "https://www.nseindia.com/-"
          },
          {
            "id": "announcement:b156f7a0e17f5d8f868e210634bb6ce12c4e35263936c29f2d8aa7356fe2f220",
            "headline": "General Updates",
            "occurred_at": "2026-10-31T14:44:24Z",
            "source_reference": "106838574",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/SUNSEC_31102026201341_SEIntimationforVR_-_31_October_2026.pdf"
          },
          {
            "id": "announcement:699b62d5b25c54c4c0fd4ef41c82e15aed8c56cc1f2d3044d9ca78309e918ac3",
            "headline": "Copy of Newspaper Publication",
            "occurred_at": "2026-10-31T12:02:02Z",
            "source_reference": "106838334",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/SUNSEC_31102026173121_SEIntimationforFinancialResultsNewspaperadvertisement.pdf"
          },
          {
            "id": "announcement:2e8c97e4c973dc87cde29e4051ea3ac05199b0030ac1d62d485a8ceaf915c0b5",
            "headline": "Outcome of Board Meeting",
            "occurred_at": "2026-10-30T08:45:10Z",
            "source_reference": "106836275",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/SUNSEC_30102026141321_BMOutcomeFinancialoct26signed.pdf"
          },
          {
            "id": "announcement:0ca57b152fd5d2b9dc7c79b597682475e24391aa185887421184f53ad540335a",
            "headline": "Allotment of Securities",
            "occurred_at": "2026-10-26T07:00:34Z",
            "source_reference": "106828196",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/SUNSEC_26102026122925_SE_Intimation_of_allotment_of_NCDs_26_Oct_2026.pdf"
          },
          {
            "id": "announcement:780835c281f68e179e2aed55704a6f02d49273f502608080ca83affd59cfa5a2",
            "headline": "Certificate under SEBI (Depositories and Participants) Regulations, 2018",
            "occurred_at": "2026-10-14T12:08:55Z",
            "source_reference": "106817485",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/SUNSEC_14102026173741_SEintimationfor74signed.pdf"
          },
          {
            "id": "announcement:08fad29aae33eceaf7803d33bf5f45c1acfe4a331c2c96cab0e58c670862fe51",
            "headline": "Resignation",
            "occurred_at": "2026-10-12T14:35:00Z",
            "source_reference": "106815017",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/SUNSEC_12102026200413_BMOutcome12October2026.pdf"
          }
        ]
      }
    },
    {
      "id": "routine:bd4ba46650d189a5317fc79b",
      "ticker": "TRENT",
      "company_name": "Trent Limited",
      "kind": "filing",
      "category": "unclassified",
      "headline": "9 routine unclassified disclosures",
      "summary": "9 lower-materiality disclosures of this category are grouped here; expand for the individual filings.",
      "priority": "low",
      "occurred_at": "2026-11-02T07:56:56Z",
      "citations": [
        {
          "document": "106839393",
          "locator": "2026-11-02T07:56:56Z",
          "quote": "Copy of Newspaper Publication"
        },
        {
          "document": "106834503",
          "locator": "2026-10-29T11:02:13Z",
          "quote": "Appointment"
        },
        {
          "document": "106834505",
          "locator": "2026-10-29T11:02:13Z",
          "quote": "Retirement"
        },
        {
          "document": "106834504",
          "locator": "2026-10-29T11:02:13Z",
          "quote": "Change in Director(s)"
        },
        {
          "document": "106834418",
          "locator": "2026-10-29T10:38:05Z",
          "quote": "Outcome of Board Meeting"
        },
        {
          "document": "106826976",
          "locator": "2026-10-23T14:18:20Z",
          "quote": "Sale or disposal"
        },
        {
          "document": "106826524",
          "locator": "2026-10-23T11:04:41Z",
          "quote": "General Updates"
        },
        {
          "document": "106821444",
          "locator": "2026-10-18T13:17:05Z",
          "quote": "Resignation"
        },
        {
          "document": "106806942",
          "locator": "2026-10-05T09:22:55Z",
          "quote": "Certificate under SEBI (Depositories and Participants) Regulations, 2018"
        }
      ],
      "materiality_score": 1.0,
      "source_reference": null,
      "attachment_url": null,
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:52:30Z",
      "demo_mode": false,
      "rank_score": 40.84,
      "rank_reasons": [
        "Source materiality 1/10",
        "Category significance 1/9",
        "Company is marked in the portfolio",
        "Recency 9.84/10",
        "Supporting details available"
      ],
      "collapsed_count": 9,
      "supporting_details": {
        "grouped_events": [
          {
            "id": "announcement:b340a0f12fbfd7ae3bc3fb442c4eebbcbf85ffe75598cc143a10459bc7239cae",
            "headline": "Copy of Newspaper Publication",
            "occurred_at": "2026-11-02T07:56:56Z",
            "source_reference": "106839393",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/TRENT_02112026132637_Q2FY27_Financial_Results_-_Newspaper_Publication.pdf"
          },
          {
            "id": "announcement:3608fd0336eec0456a7c4f1fc59cbb0384e5c1f26fa0eb7dbbee12a11fed187b",
            "headline": "Appointment",
            "occurred_at": "2026-10-29T11:02:13Z",
            "source_reference": "106834503",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/TRENT_29102026163044_AppointmentofDirector.pdf"
          },
          {
            "id": "announcement:46e901df1fa97b680b6616fd9fa5a6ac150bbb811834adeb4b71730d36c37cdb",
            "headline": "Retirement",
            "occurred_at": "2026-10-29T11:02:13Z",
            "source_reference": "106834505",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/TRENT_29102026163122_AppointmentofDirector.pdf"
          },
          {
            "id": "announcement:bcdbc54104b49d8910c16cf5d34a5a14ff33e9209a075f1d027ee2993e2a9bef",
            "headline": "Change in Director(s)",
            "occurred_at": "2026-10-29T11:02:13Z",
            "source_reference": "106834504",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/TRENT_29102026163102_AppointmentofDirector.pdf"
          },
          {
            "id": "announcement:08f52d0517afd2e18fc8d14ef0fe835f5c03a3786a7dc88864688f33987b4995",
            "headline": "Outcome of Board Meeting",
            "occurred_at": "2026-10-29T10:38:05Z",
            "source_reference": "106834418",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/TRENT_29102026160446_DraftOutcomeofBM.pdf"
          },
          {
            "id": "announcement:db2770bbc1ae3611b37e3770c46dafbaf30289db47548b71e35e9c651b4e4c4e",
            "headline": "Sale or disposal",
            "occurred_at": "2026-10-23T14:18:20Z",
            "source_reference": "106826976",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/TRENT_23102026194710_Reg30DivestmentofstepdownsubsidiaryofNahar.pdf"
          },
          {
            "id": "announcement:cf88d773c539c9157296e4a8e6ee914e692343882a6e1f5a983ec45d39d21bbf",
            "headline": "General Updates",
            "occurred_at": "2026-10-23T11:04:41Z",
            "source_reference": "106826524",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/TRENT_23102026163319_Reg30Reminderlettertoshareholder2026.pdf"
          },
          {
            "id": "announcement:498efae5477db40a7fd9b210864b2b43bdf70689632fbfbc9f78135ace4ebd4b",
            "headline": "Resignation",
            "occurred_at": "2026-10-18T13:17:05Z",
            "source_reference": "106821444",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/TRENT_18102026184315_Intimation_of_Resignation_of_NED.pdf"
          },
          {
            "id": "announcement:b601c895ceed75464c9d7d4a6ae178c6b861e3ca505a2bb347606e2ec48bfa3a",
            "headline": "Certificate under SEBI (Depositories and Participants) Regulations, 2018",
            "occurred_at": "2026-10-05T09:22:55Z",
            "source_reference": "106806942",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/TRENT_05102026145012_Letter_to_Stock_Exchange_-_Reg_74_5_.pdf"
          }
        ]
      }
    },
    {
      "id": "routine:54d29c8ecd468502243c4dff",
      "ticker": "LT",
      "company_name": "Larsen & Toubro Limited",
      "kind": "filing",
      "category": "unclassified",
      "headline": "8 routine unclassified disclosures",
      "summary": "8 lower-materiality disclosures of this category are grouped here; expand for the individual filings.",
      "priority": "low",
      "occurred_at": "2026-11-02T04:48:49Z",
      "citations": [
        {
          "document": "106839016",
          "locator": "2026-11-02T04:48:49Z",
          "quote": "Bagging/Receiving of orders/contracts"
        },
        {
          "document": "106837941",
          "locator": "2026-10-31T07:30:35Z",
          "quote": "General Updates"
        },
        {
          "document": "106833097",
          "locator": "2026-10-28T14:17:25Z",
          "quote": "Copy of Newspaper Publication"
        },
        {
          "document": "106830809",
          "locator": "2026-10-27T13:07:19Z",
          "quote": "Updates"
        },
        {
          "document": "106830479",
          "locator": "2026-10-27T11:43:09Z",
          "quote": "Outcome of Board Meeting"
        },
        {
          "document": "106829991",
          "locator": "2026-10-27T07:59:18Z",
          "quote": "Allotment of Securities"
        },
        {
          "document": "106814880",
          "locator": "2026-10-12T13:00:27Z",
          "quote": "Certificate under SEBI (Depositories and Participants) Regulations, 2018"
        },
        {
          "document": "106810362",
          "locator": "2026-10-07T15:59:23Z",
          "quote": "Change in Management"
        }
      ],
      "materiality_score": 1.0,
      "source_reference": null,
      "attachment_url": null,
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:52:03Z",
      "demo_mode": false,
      "rank_score": 40.83,
      "rank_reasons": [
        "Source materiality 1/10",
        "Category significance 1/9",
        "Company is marked in the portfolio",
        "Recency 9.83/10",
        "Supporting details available"
      ],
      "collapsed_count": 8,
      "supporting_details": {
        "grouped_events": [
          {
            "id": "announcement:dd43dd3cd8483933e43bb9c39c12c963834afa03d2713dceadbf5fad2aabb242",
            "headline": "Bagging/Receiving of orders/contracts",
            "occurred_at": "2026-11-02T04:48:49Z",
            "source_reference": "106839016",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/PAM_02112026101835_PressRelease02112026.pdf"
          },
          {
            "id": "announcement:e54e3dcfbd304ee1e37068e63cb2eed26a794d69e587ff860de029142b00b6f1",
            "headline": "General Updates",
            "occurred_at": "2026-10-31T07:30:35Z",
            "source_reference": "106837941",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/AB_31102026130022_SEIntimation_ExtensionofBTAVyoma_31102026.pdf"
          },
          {
            "id": "announcement:9e127dfb8c811781fb78f4fad49922b009939569a5c4ceeb52a8be9125468701",
            "headline": "Copy of Newspaper Publication",
            "occurred_at": "2026-10-28T14:17:25Z",
            "source_reference": "106833097",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/PAM_28102026194657_NewspaperAdvtSep2026.pdf"
          },
          {
            "id": "announcement:ee9d213658485267c7ff4a3b1fc0d46bfe7685b82471487f5d95cdb7d0bc7fe8",
            "headline": "Updates",
            "occurred_at": "2026-10-27T13:07:19Z",
            "source_reference": "106830809",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/PAM_27102026183653_AnalystPresentationSep2026.pdf"
          },
          {
            "id": "announcement:595c69ab126e7463688e7b9e7bac256ae48b9ab6c06c31016b994f7859ad46ac",
            "headline": "Outcome of Board Meeting",
            "occurred_at": "2026-10-27T11:43:09Z",
            "source_reference": "106830479",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/PAM_27102026171156_LTSep2026.pdf"
          },
          {
            "id": "announcement:11443b2589cc0a842cbcb9eb0f3740ac8541c185e8cedb49d983109fea1fdeac",
            "headline": "Allotment of Securities",
            "occurred_at": "2026-10-27T07:59:18Z",
            "source_reference": "106829991",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/PAM_27102026132854_ESOPAllotment27102026.pdf"
          },
          {
            "id": "announcement:7ee70d99c47cb788533896d95dd50a077c65398657854eda48a36481c2fef101",
            "headline": "Certificate under SEBI (Depositories and Participants) Regulations, 2018",
            "occurred_at": "2026-10-12T13:00:27Z",
            "source_reference": "106814880",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/PAM_12102026183004_Intimation745Sep2026.pdf"
          },
          {
            "id": "announcement:0de7171aa5484c0eb9b063db444f16ba089a41408b221e97f5be5424518ad1fe",
            "headline": "Change in Management",
            "occurred_at": "2026-10-07T15:59:23Z",
            "source_reference": "106810362",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/PAM_07102026212904_IntimationSRMGT07102026.pdf"
          }
        ]
      }
    },
    {
      "id": "routine:7278cd794edcbbd504073108",
      "ticker": "MARUTI",
      "company_name": "Maruti Suzuki India Limited",
      "kind": "filing",
      "category": "unclassified",
      "headline": "4 routine unclassified disclosures",
      "summary": "4 lower-materiality disclosures of this category are grouped here; expand for the individual filings.",
      "priority": "low",
      "occurred_at": "2026-11-01T09:14:18Z",
      "citations": [
        {
          "document": "106838789",
          "locator": "2026-11-01T09:14:18Z",
          "quote": "General Updates"
        },
        {
          "document": "106831569",
          "locator": "2026-10-28T05:08:47Z",
          "quote": "Copy of Newspaper Publication"
        },
        {
          "document": "106830187",
          "locator": "2026-10-27T09:57:51Z",
          "quote": "Outcome of Board Meeting"
        },
        {
          "document": "106819161",
          "locator": "2026-10-15T13:43:00Z",
          "quote": "Action(s) taken or orders passed"
        }
      ],
      "materiality_score": 1.0,
      "source_reference": null,
      "attachment_url": null,
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:52:07Z",
      "demo_mode": false,
      "rank_score": 40.74,
      "rank_reasons": [
        "Source materiality 1/10",
        "Category significance 1/9",
        "Company is marked in the portfolio",
        "Recency 9.74/10",
        "Supporting details available"
      ],
      "collapsed_count": 4,
      "supporting_details": {
        "grouped_events": [
          {
            "id": "announcement:0057d81fe1783a4c95631401b1bda6855b43884c684d64e875919f5f5b9d3bd3",
            "headline": "General Updates",
            "occurred_at": "2026-11-01T09:14:18Z",
            "source_reference": "106838789",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/MARUTIASHISH_01112026143647_STxIntimation_Prod_Oct2026.pdf"
          },
          {
            "id": "announcement:56dc96a887f9159e1861934f9c6c33f43b8709abd409b09393db3018a77f0c84",
            "headline": "Copy of Newspaper Publication",
            "occurred_at": "2026-10-28T05:08:47Z",
            "source_reference": "106831569",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/MARUTI_28102026103729_STxIntimation_NP_27Oct2026.pdf"
          },
          {
            "id": "announcement:83f7d6ad2f0b13e9782164d47c2ac0ff76ee5d60aa9732b031b735c37a281a88",
            "headline": "Outcome of Board Meeting",
            "occurred_at": "2026-10-27T09:57:51Z",
            "source_reference": "106830187",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/MARUTI_27102026152412_QuickResults_27Oct2026_signed.pdf"
          },
          {
            "id": "announcement:0ac13e57bbc0df39bc09c266c78d096d1100a1395a1000ea0686524c43c755bc",
            "headline": "Action(s) taken or orders passed",
            "occurred_at": "2026-10-15T13:43:00Z",
            "source_reference": "106819161",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/MARUTI_15102026191103_Intimation_15102026.pdf"
          }
        ]
      }
    },
    {
      "id": "routine:649a6c8735f5afeb0c7a3b47",
      "ticker": "HDFCBANK",
      "company_name": "HDFC Bank Limited",
      "kind": "filing",
      "category": "unclassified",
      "headline": "7 routine unclassified disclosures",
      "summary": "7 lower-materiality disclosures of this category are grouped here; expand for the individual filings.",
      "priority": "low",
      "occurred_at": "2026-10-31T16:46:44Z",
      "citations": [
        {
          "document": "106838688",
          "locator": "2026-10-31T16:46:44Z",
          "quote": "Change in Management"
        },
        {
          "document": "106836184",
          "locator": "2026-10-30T07:54:25Z",
          "quote": "ESOP/ESOS/ESPS"
        },
        {
          "document": "106829496",
          "locator": "2026-10-27T02:32:54Z",
          "quote": "General Updates"
        },
        {
          "document": "106824495",
          "locator": "2026-10-22T06:25:18Z",
          "quote": "Copy of Newspaper Publication"
        },
        {
          "document": "106823131",
          "locator": "2026-10-21T06:22:36Z",
          "quote": "Shareholders meeting"
        },
        {
          "document": "106821066",
          "locator": "2026-10-17T08:26:22Z",
          "quote": "Outcome of Board Meeting"
        },
        {
          "document": "106820256",
          "locator": "2026-10-16T11:05:12Z",
          "quote": "Certificate under SEBI (Depositories and Participants) Regulations, 2018"
        }
      ],
      "materiality_score": 1.0,
      "source_reference": null,
      "attachment_url": null,
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:51:50Z",
      "demo_mode": false,
      "rank_score": 40.66,
      "rank_reasons": [
        "Source materiality 1/10",
        "Category significance 1/9",
        "Company is marked in the portfolio",
        "Recency 9.66/10",
        "Supporting details available"
      ],
      "collapsed_count": 7,
      "supporting_details": {
        "grouped_events": [
          {
            "id": "announcement:a573afeb38ef858bfe32e10e1c34ab2b866401d10e01cc99173aad5a4a1ec606",
            "headline": "Change in Management",
            "occurred_at": "2026-10-31T16:46:44Z",
            "source_reference": "106838688",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/HDFCBANK3_31102026221631_SE_INTIMATION-_Sanjay_Dsouza.pdf"
          },
          {
            "id": "announcement:559faf3a211e828fac96381589e1926f4d43fcf169681801202bb9c2ede46096",
            "headline": "ESOP/ESOS/ESPS",
            "occurred_at": "2026-10-30T07:54:25Z",
            "source_reference": "106836184",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/HDFCBANK_30102026132409_SELetterESOP30102026.pdf"
          },
          {
            "id": "announcement:0bd5e06a02b3fe7f61bb1841142155833c9a7c74bf9dc754c0eb5c4210e7b23a",
            "headline": "General Updates",
            "occurred_at": "2026-10-27T02:32:54Z",
            "source_reference": "106829496",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/HDFCBANK_27102026080232_SEIntimation_appt_of_AB.pdf"
          },
          {
            "id": "announcement:bc8fbf90f6cceb8e68495550130cc527cc81f1c1e6eb11f7e1379b516c38bde3",
            "headline": "Copy of Newspaper Publication",
            "occurred_at": "2026-10-22T06:25:18Z",
            "source_reference": "106824495",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/HDFCBANK3_22102026115451_PB_adv_22102026.pdf"
          },
          {
            "id": "announcement:375a3330872299473a92bf9d729cb0b022f2ad6ef38f7b370f36ea8c04a9ca61",
            "headline": "Shareholders meeting",
            "occurred_at": "2026-10-21T06:22:36Z",
            "source_reference": "106823131",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/HDFCBANK3_21102026115151_SEIntimationPostalBallotNoticeOct2026.pdf"
          },
          {
            "id": "announcement:718186501751115bc55d28296104946b7cecb45ee5ead470e8492a850057f265",
            "headline": "Outcome of Board Meeting",
            "occurred_at": "2026-10-17T08:26:22Z",
            "source_reference": "106821066",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/HDFCBANK_17102026135520_OutcomeofBMResults_17oct2026.pdf"
          },
          {
            "id": "announcement:52f0d18060830cce8a57b4f9335151c6910c91b1fcf02e7fb91b44486ad36740",
            "headline": "Certificate under SEBI (Depositories and Participants) Regulations, 2018",
            "occurred_at": "2026-10-16T11:05:12Z",
            "source_reference": "106820256",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/HDFCBANK_16102026162906_SEintimatiomReg74_530Sep2025.pdf"
          }
        ]
      }
    },
    {
      "id": "routine:96bd4c8286aab29b2a62be36",
      "ticker": "RELIANCE",
      "company_name": "Reliance Industries Limited",
      "kind": "filing",
      "category": "unclassified",
      "headline": "6 routine unclassified disclosures",
      "summary": "6 lower-materiality disclosures of this category are grouped here; expand for the individual filings.",
      "priority": "low",
      "occurred_at": "2026-10-30T14:10:11Z",
      "citations": [
        {
          "document": "106837394",
          "locator": "2026-10-30T14:10:11Z",
          "quote": "Outcome of Board Meeting"
        },
        {
          "document": "106833561",
          "locator": "2026-10-29T03:25:40Z",
          "quote": "Other Restructuring"
        },
        {
          "document": "106831152",
          "locator": "2026-10-27T16:41:29Z",
          "quote": "General Updates"
        },
        {
          "document": "106823997",
          "locator": "2026-10-21T17:14:39Z",
          "quote": "Updates"
        },
        {
          "document": "106820709",
          "locator": "2026-10-16T15:28:26Z",
          "quote": "Copy of Newspaper Publication"
        },
        {
          "document": "106810410",
          "locator": "2026-10-07T17:06:08Z",
          "quote": "Action(s) taken or orders passed"
        }
      ],
      "materiality_score": 1.0,
      "source_reference": null,
      "attachment_url": null,
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:51:10Z",
      "demo_mode": false,
      "rank_score": 40.54,
      "rank_reasons": [
        "Source materiality 1/10",
        "Category significance 1/9",
        "Company is marked in the portfolio",
        "Recency 9.54/10",
        "Supporting details available"
      ],
      "collapsed_count": 6,
      "supporting_details": {
        "grouped_events": [
          {
            "id": "announcement:ff41da1095ee04432af48210268f99b373a5b6392fd4b130559c736d33230f07",
            "headline": "Outcome of Board Meeting",
            "occurred_at": "2026-10-30T14:10:11Z",
            "source_reference": "106837394",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/kavinavora_30102026193935_SE_30102026_Results.pdf"
          },
          {
            "id": "announcement:d076531f172a0f3fd65e16a3fd6f767523c5297961650b7e82bf05e0d33890bd",
            "headline": "Other Restructuring",
            "occurred_at": "2026-10-29T03:25:40Z",
            "source_reference": "106833561",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/kavinavora_29102026084603_SE_29102026.pdf"
          },
          {
            "id": "announcement:0e4887d46aa5bfe09b953dd045bfb78fe660d824fd1bbed7979db86444781897",
            "headline": "General Updates",
            "occurred_at": "2026-10-27T16:41:29Z",
            "source_reference": "106831152",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/kavinavora_27102026220855_RIL_SELETTER_271026.pdf"
          },
          {
            "id": "announcement:3d2664f03c5837603dd7b65645cb670710ce2114988b0808b3e5f63dedcdf0d7",
            "headline": "Updates",
            "occurred_at": "2026-10-21T17:14:39Z",
            "source_reference": "106823997",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/kavinavora_21102026224413_SE_21102026.pdf"
          },
          {
            "id": "announcement:d071b975959739aa4215e0a321654f8361caea0ab7293b3189323d8ae5f008d0",
            "headline": "Copy of Newspaper Publication",
            "occurred_at": "2026-10-16T15:28:26Z",
            "source_reference": "106820709",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/kavinavora_16102026205736_RILSELetter_16102026.pdf"
          },
          {
            "id": "announcement:a2bc672a0dc38f567426646f5dcba653a7f096d126875aacb4f983afb50dc504",
            "headline": "Action(s) taken or orders passed",
            "occurred_at": "2026-10-07T17:06:08Z",
            "source_reference": "106810410",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/PVIVINMA_07102026223504_RIL_SEletter07102026.pdf"
          }
        ]
      }
    },
    {
      "id": "routine:42db79ac0f521be630372f64",
      "ticker": "INFY",
      "company_name": "Infosys Limited",
      "kind": "filing",
      "category": "unclassified",
      "headline": "5 routine unclassified disclosures",
      "summary": "5 lower-materiality disclosures of this category are grouped here; expand for the individual filings.",
      "priority": "low",
      "occurred_at": "2026-10-30T13:20:50Z",
      "citations": [
        {
          "document": "106837197",
          "locator": "2026-10-30T13:20:50Z",
          "quote": "Updates"
        },
        {
          "document": "106834249",
          "locator": "2026-10-29T09:45:01Z",
          "quote": "Copy of Newspaper Publication"
        },
        {
          "document": "106826469",
          "locator": "2026-10-23T10:40:52Z",
          "quote": "Record Date"
        },
        {
          "document": "106826465",
          "locator": "2026-10-23T10:38:26Z",
          "quote": "Outcome of Board Meeting"
        },
        {
          "document": "106813727",
          "locator": "2026-10-10T17:15:31Z",
          "quote": "General Updates"
        }
      ],
      "materiality_score": 1.0,
      "source_reference": null,
      "attachment_url": null,
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:51:58Z",
      "demo_mode": false,
      "rank_score": 40.53,
      "rank_reasons": [
        "Source materiality 1/10",
        "Category significance 1/9",
        "Company is marked in the portfolio",
        "Recency 9.53/10",
        "Supporting details available"
      ],
      "collapsed_count": 5,
      "supporting_details": {
        "grouped_events": [
          {
            "id": "announcement:325184187435396f433801d9d46c2e46fdaf29fe2523907151bc6264ec08424f",
            "headline": "Updates",
            "occurred_at": "2026-10-30T13:20:50Z",
            "source_reference": "106837197",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/INFY_30102026185037_PR_30102026.pdf"
          },
          {
            "id": "announcement:114c429af5b5a05e3d3a24aa65c55f004763ec5ab3453ec9a8a8159e09c6913d",
            "headline": "Copy of Newspaper Publication",
            "occurred_at": "2026-10-29T09:45:01Z",
            "source_reference": "106834249",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/INFY_29102026151445_SE_intimation_Newspaper_ad_2.pdf"
          },
          {
            "id": "announcement:e3ad5b26b54d8f5e6755c98fd0e8c08674e3ddcdf094052677eee7c0b964a214",
            "headline": "Record Date",
            "occurred_at": "2026-10-23T10:40:52Z",
            "source_reference": "106826469",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/Infosys_23102026160926_BM_Outcome_Oct232026_1.pdf"
          },
          {
            "id": "announcement:f29e9cdd4aa2b5d463fa32a03de687f62c9e3be96b50247f6dbf2a6dcabc4978",
            "headline": "Outcome of Board Meeting",
            "occurred_at": "2026-10-23T10:38:26Z",
            "source_reference": "106826465",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/Infosys_23102026160704_BM_Outcome_Oct232026_1.pdf"
          },
          {
            "id": "announcement:32a3283ad1cb441cd7bec03ca2cceef0f4a613fc10f9c78c24415813da82d34b",
            "headline": "General Updates",
            "occurred_at": "2026-10-10T17:15:31Z",
            "source_reference": "106813727",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/INFY_10102026224330_Infosys_October102026.pdf"
          }
        ]
      }
    },
    {
      "id": "routine:e89470c83603decdcfb73a72",
      "ticker": "HINDUNILVR",
      "company_name": "Hindustan Unilever Limited",
      "kind": "filing",
      "category": "unclassified",
      "headline": "6 routine unclassified disclosures",
      "summary": "6 lower-materiality disclosures of this category are grouped here; expand for the individual filings.",
      "priority": "low",
      "occurred_at": "2026-10-30T12:47:40Z",
      "citations": [
        {
          "document": "106837067",
          "locator": "2026-10-30T12:47:40Z",
          "quote": "Copy of Newspaper Publication"
        },
        {
          "document": "106831528",
          "locator": "2026-10-28T04:42:52Z",
          "quote": "General Updates"
        },
        {
          "document": "106831498",
          "locator": "2026-10-28T04:18:00Z",
          "quote": "Record Date"
        },
        {
          "document": "106831491",
          "locator": "2026-10-28T04:15:35Z",
          "quote": "Dividend"
        },
        {
          "document": "106831488",
          "locator": "2026-10-28T04:08:34Z",
          "quote": "Outcome of Board Meeting"
        },
        {
          "document": "106811696",
          "locator": "2026-10-08T14:09:31Z",
          "quote": "Certificate under SEBI (Depositories and Participants) Regulations, 2018"
        }
      ],
      "materiality_score": 1.0,
      "source_reference": null,
      "attachment_url": null,
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:51:52Z",
      "demo_mode": false,
      "rank_score": 40.53,
      "rank_reasons": [
        "Source materiality 1/10",
        "Category significance 1/9",
        "Company is marked in the portfolio",
        "Recency 9.53/10",
        "Supporting details available"
      ],
      "collapsed_count": 6,
      "supporting_details": {
        "grouped_events": [
          {
            "id": "announcement:f1ebf2dd5fc01876999c404bd9378ac15fa07902b7d986137d9a807bd7e6b613",
            "headline": "Copy of Newspaper Publication",
            "occurred_at": "2026-10-30T12:47:40Z",
            "source_reference": "106837067",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/HINDUNILVR_30102026181553_SEIntimationNewspaperADRecordDatesigned.pdf"
          },
          {
            "id": "announcement:162ee4c1afbfb267dd01d56681954556db90e4b0c54aadff9f72a13c43416df1",
            "headline": "General Updates",
            "occurred_at": "2026-10-28T04:42:52Z",
            "source_reference": "106831528",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/HINDUNILVR_28102026101021_SEIntimationMinimalistsigned.pdf"
          },
          {
            "id": "announcement:add68889f847266c95f91d1d744644e7dae6b274d1fc54eb8a2772b0ca6acc64",
            "headline": "Record Date",
            "occurred_at": "2026-10-28T04:18:00Z",
            "source_reference": "106831498",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/HINDUNILVR_28102026094634_SEIntimationOutcomeofBM28102026signed.pdf"
          },
          {
            "id": "announcement:ad776c3ab753d6a60cfc232411c0b5c39a1ec58d445271e738c01c9b439e90f1",
            "headline": "Dividend",
            "occurred_at": "2026-10-28T04:15:35Z",
            "source_reference": "106831491",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/HINDUNILVR_28102026094439_SEIntimationOutcomeofBM28102026signed.pdf"
          },
          {
            "id": "announcement:1cd4c5a6de44a6b9e4a3b4b2091f9ad2bf772e446d418c730c5f23b83d15c3b3",
            "headline": "Outcome of Board Meeting",
            "occurred_at": "2026-10-28T04:08:34Z",
            "source_reference": "106831488",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/HINDUNILVR_28102026093630_SEIntimationOutcomeofBM28102026signed.pdf"
          },
          {
            "id": "announcement:014c1fb8d01abd110840dce32a3ae7e9c1536412df31b5d2e03a68780b7c33df",
            "headline": "Certificate under SEBI (Depositories and Participants) Regulations, 2018",
            "occurred_at": "2026-10-08T14:09:31Z",
            "source_reference": "106811696",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/HINDUNILVR_08102026193903_Regulation74_5_Intimationsigned.pdf"
          }
        ]
      }
    },
    {
      "id": "routine:fbf9d7b475e6cfd65ed8046c",
      "ticker": "TITAN",
      "company_name": "Titan Company Limited",
      "kind": "filing",
      "category": "unclassified",
      "headline": "4 routine unclassified disclosures",
      "summary": "4 lower-materiality disclosures of this category are grouped here; expand for the individual filings.",
      "priority": "low",
      "occurred_at": "2026-10-28T11:56:00Z",
      "citations": [
        {
          "document": "106832541",
          "locator": "2026-10-28T11:56:00Z",
          "quote": "Copy of Newspaper Publication"
        },
        {
          "document": "106822009",
          "locator": "2026-10-19T10:41:44Z",
          "quote": "General Updates"
        },
        {
          "document": "106815390",
          "locator": "2026-10-13T04:53:55Z",
          "quote": "Certificate under SEBI (Depositories and Participants) Regulations, 2018"
        },
        {
          "document": "106811243",
          "locator": "2026-10-08T10:42:50Z",
          "quote": "Updates"
        }
      ],
      "materiality_score": 1.0,
      "source_reference": null,
      "attachment_url": null,
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:52:28Z",
      "demo_mode": false,
      "rank_score": 40.31,
      "rank_reasons": [
        "Source materiality 1/10",
        "Category significance 1/9",
        "Company is marked in the portfolio",
        "Recency 9.31/10",
        "Supporting details available"
      ],
      "collapsed_count": 4,
      "supporting_details": {
        "grouped_events": [
          {
            "id": "announcement:f062aff528840372537ded0a7b3bc198263aaa9b8723d9ef8bf6640e8e2ad7d0",
            "headline": "Copy of Newspaper Publication",
            "occurred_at": "2026-10-28T11:56:00Z",
            "source_reference": "106832541",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/TITAN_28102026172546_SEnewspaperadlossofshares.pdf"
          },
          {
            "id": "announcement:2b041cb3352dfb10770fae0232daaa43cfc9c064420fbf8699da5797c74c74c2",
            "headline": "General Updates",
            "occurred_at": "2026-10-19T10:41:44Z",
            "source_reference": "106822009",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/TITAN_19102026161128_SECPRedemption16102026.pdf"
          },
          {
            "id": "announcement:3ee24ab01b2122fd6ba61db8d650e3f0bca6aba0ecc89917e5accf120b6ef61a",
            "headline": "Certificate under SEBI (Depositories and Participants) Regulations, 2018",
            "occurred_at": "2026-10-13T04:53:55Z",
            "source_reference": "106815390",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/TITAN_13102026102335_SERegulation745.pdf"
          },
          {
            "id": "announcement:b4e0fb49b8a60926cca230213ad0920093bfac4b771c3a9ee02c3e18b8bbc3b9",
            "headline": "Updates",
            "occurred_at": "2026-10-08T10:42:50Z",
            "source_reference": "106811243",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/TITAN_08102026161235_SECPRedemption08102026.pdf"
          }
        ]
      }
    },
    {
      "id": "routine:2a999ec3c64e4729a3249d46",
      "ticker": "POLYCAB",
      "company_name": "Polycab India Limited",
      "kind": "filing",
      "category": "unclassified",
      "headline": "5 routine unclassified disclosures",
      "summary": "5 lower-materiality disclosures of this category are grouped here; expand for the individual filings.",
      "priority": "low",
      "occurred_at": "2026-11-03T10:31:15Z",
      "citations": [
        {
          "document": "106841885",
          "locator": "2026-11-03T10:31:15Z",
          "quote": "ESOP/ESOS/ESPS"
        },
        {
          "document": "106836029",
          "locator": "2026-10-30T06:50:09Z",
          "quote": "Corporate Insolvency Resolution Process"
        },
        {
          "document": "106832611",
          "locator": "2026-10-28T12:13:39Z",
          "quote": "General Updates"
        },
        {
          "document": "106830830",
          "locator": "2026-10-27T13:12:35Z",
          "quote": "Certificate under SEBI (Depositories and Participants) Regulations, 2018"
        },
        {
          "document": "106818441",
          "locator": "2026-10-15T07:28:53Z",
          "quote": "Outcome of Board Meeting"
        }
      ],
      "materiality_score": 0.0,
      "source_reference": null,
      "attachment_url": null,
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-03T17:06:48Z",
      "demo_mode": false,
      "rank_score": 30.97,
      "rank_reasons": [
        "Source materiality 0/10",
        "Category significance 1/9",
        "Company is marked in the portfolio",
        "Recency 9.97/10",
        "Supporting details available"
      ],
      "collapsed_count": 5,
      "supporting_details": {
        "grouped_events": [
          {
            "id": "announcement:97374c74fa54f04517e5121fface7d001494c69c9eb112a7b79631b38fb4b025",
            "headline": "ESOP/ESOS/ESPS",
            "occurred_at": "2026-11-03T10:31:15Z",
            "source_reference": "106841885",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/POLYCAB_03112026160106_IntimationtoStockexchange.pdf"
          },
          {
            "id": "announcement:bbab2682cb0b13eafbec95caa127a382adb01315d272acc7a01704f386d47c4a",
            "headline": "Corporate Insolvency Resolution Process",
            "occurred_at": "2026-10-30T06:50:09Z",
            "source_reference": "106836029",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/POLYCAB_30102026121954_SECIRP30102026.pdf"
          },
          {
            "id": "announcement:f1a4f416705f784e23f13c1b3458bcbb7e76a42e5c09c031e99ec30b151bac31",
            "headline": "General Updates",
            "occurred_at": "2026-10-28T12:13:39Z",
            "source_reference": "106832611",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/POLYCAB_28102026174326_Intimationtostockexchange.pdf"
          },
          {
            "id": "announcement:d1a2585adffafdaf06a59b6c8fb052103ac91ebfd8fcff91c60c28f5c67a42d0",
            "headline": "Certificate under SEBI (Depositories and Participants) Regulations, 2018",
            "occurred_at": "2026-10-27T13:12:35Z",
            "source_reference": "106830830",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/POLYCAB_27102026184209_IntimationtoStockExchange.pdf"
          },
          {
            "id": "announcement:bccafdb36599a22307a415c5dfa1e79bbe79e2a39558e9a6d86cfd320efc9889",
            "headline": "Outcome of Board Meeting",
            "occurred_at": "2026-10-15T07:28:53Z",
            "source_reference": "106818441",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/POLYCAB_15102026125737_OutcomeofBoardMeeting.pdf"
          }
        ]
      }
    },
    {
      "id": "routine:665de5315ce6ad3ee3d413bb",
      "ticker": "ICICIBANK",
      "company_name": "ICICI Bank Limited",
      "kind": "filing",
      "category": "unclassified",
      "headline": "4 routine unclassified disclosures",
      "summary": "4 lower-materiality disclosures of this category are grouped here; expand for the individual filings.",
      "priority": "low",
      "occurred_at": "2026-11-03T04:54:40Z",
      "citations": [
        {
          "document": "106841159",
          "locator": "2026-11-03T04:54:40Z",
          "quote": "ESOP/ESOS/ESPS"
        },
        {
          "document": "106838744",
          "locator": "2026-11-01T04:13:51Z",
          "quote": "General Updates"
        },
        {
          "document": "106821131",
          "locator": "2026-10-17T09:58:05Z",
          "quote": "Outcome of Board Meeting"
        },
        {
          "document": "106811462",
          "locator": "2026-10-08T12:07:19Z",
          "quote": "Certificate under SEBI (Depositories and Participants) Regulations, 2018"
        }
      ],
      "materiality_score": 0.0,
      "source_reference": null,
      "attachment_url": null,
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-03T17:06:31Z",
      "demo_mode": false,
      "rank_score": 30.94,
      "rank_reasons": [
        "Source materiality 0/10",
        "Category significance 1/9",
        "Company is marked in the portfolio",
        "Recency 9.94/10",
        "Supporting details available"
      ],
      "collapsed_count": 4,
      "supporting_details": {
        "grouped_events": [
          {
            "id": "announcement:90e38a8d92bcbc4dd5fc273c4e013091b1b53293ef9379cee48ae4fa239df895",
            "headline": "ESOP/ESOS/ESPS",
            "occurred_at": "2026-11-03T04:54:40Z",
            "source_reference": "106841159",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/ICICIBANK1_03112026102424_Lettertoexchange.pdf"
          },
          {
            "id": "announcement:80e3eee157538e583d495d57685d0f71fba5535fa8365966b67e1dcc09bd06f0",
            "headline": "General Updates",
            "occurred_at": "2026-11-01T04:13:51Z",
            "source_reference": "106838744",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/ICICI2022_01112026094235_BSENSE01112026.pdf"
          },
          {
            "id": "announcement:3b0f05c5fa454dc57da24e048e08b08549eb662f9b711d45326c47931685a37c",
            "headline": "Outcome of Board Meeting",
            "occurred_at": "2026-10-17T09:58:05Z",
            "source_reference": "106821131",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/ICICI2022_17102026152608_NSEBSE17102026.pdf"
          },
          {
            "id": "announcement:61b7970c8448617f1dd5e9fea3af8b1918282272963a205f74e1341b1ed1600b",
            "headline": "Certificate under SEBI (Depositories and Participants) Regulations, 2018",
            "occurred_at": "2026-10-08T12:07:19Z",
            "source_reference": "106811462",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/ICICIBANK1_08102026173642_Regulation_74_5__Certificate_NSE_BSE_20260930-BONDS.pdf"
          }
        ]
      }
    },
    {
      "id": "routine:25649ee65d418662e20f344f",
      "ticker": "ITC",
      "company_name": "ITC Limited",
      "kind": "filing",
      "category": "unclassified",
      "headline": "4 routine unclassified disclosures",
      "summary": "4 lower-materiality disclosures of this category are grouped here; expand for the individual filings.",
      "priority": "low",
      "occurred_at": "2026-11-02T13:02:13Z",
      "citations": [
        {
          "document": "106840335",
          "locator": "2026-11-02T13:02:13Z",
          "quote": "General Updates"
        },
        {
          "document": "106840268",
          "locator": "2026-11-02T12:50:16Z",
          "quote": "Outcome of Board Meeting"
        },
        {
          "document": "106819181",
          "locator": "2026-10-15T13:50:08Z",
          "quote": "ESOP/ESOS/ESPS"
        },
        {
          "document": "106806918",
          "locator": "2026-10-05T08:51:07Z",
          "quote": "Certificate under SEBI (Depositories and Participants) Regulations, 2018"
        }
      ],
      "materiality_score": 0.0,
      "source_reference": null,
      "attachment_url": null,
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:52:00Z",
      "demo_mode": false,
      "rank_score": 30.87,
      "rank_reasons": [
        "Source materiality 0/10",
        "Category significance 1/9",
        "Company is marked in the portfolio",
        "Recency 9.87/10",
        "Supporting details available"
      ],
      "collapsed_count": 4,
      "supporting_details": {
        "grouped_events": [
          {
            "id": "announcement:3ef3632534b79614b7297e943b3aaa777113f4780906c3b778e6767dced1c1ae",
            "headline": "General Updates",
            "occurred_at": "2026-11-02T13:02:13Z",
            "source_reference": "106840335",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/ITC_02112026183159_SE_Media_.pdf"
          },
          {
            "id": "announcement:0177015149ce8979f511b0f4c547a82194a7f5058f680e4f8fc9ab72b7e637d9",
            "headline": "Outcome of Board Meeting",
            "occurred_at": "2026-11-02T12:50:16Z",
            "source_reference": "106840268",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/ITC_02112026181912_SE_Results_.pdf"
          },
          {
            "id": "announcement:8b1c18d6629ce050dbb407af195ff03d98af147c815c9acd26dbb23436cd7a42",
            "headline": "ESOP/ESOS/ESPS",
            "occurred_at": "2026-10-15T13:50:08Z",
            "source_reference": "106819181",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/ITC_15102026192000_SE.pdf"
          },
          {
            "id": "announcement:b48baf3b149ce899db47f54c448e387a4319df29fa873fe89df3215f42382afc",
            "headline": "Certificate under SEBI (Depositories and Participants) Regulations, 2018",
            "occurred_at": "2026-10-05T08:51:07Z",
            "source_reference": "106806918",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/ITC_05102026142025_Demat_Remat_quarterly_Sept26.pdf"
          }
        ]
      }
    },
    {
      "id": "routine:99d76b3730367aa2ee84c9cc",
      "ticker": "SUZLON",
      "company_name": "Suzlon Energy Limited",
      "kind": "filing",
      "category": "unclassified",
      "headline": "3 routine unclassified disclosures",
      "summary": "3 lower-materiality disclosures of this category are grouped here; expand for the individual filings.",
      "priority": "low",
      "occurred_at": "2026-10-29T10:21:45Z",
      "citations": [
        {
          "document": "106834353",
          "locator": "2026-10-29T10:21:45Z",
          "quote": "Outcome of Board Meeting"
        },
        {
          "document": "106823458",
          "locator": "2026-10-21T10:37:30Z",
          "quote": "ESOP/ESOS/ESPS"
        },
        {
          "document": "106812495",
          "locator": "2026-10-09T09:22:12Z",
          "quote": "Certificate under SEBI (Depositories and Participants) Regulations, 2018"
        }
      ],
      "materiality_score": 0.0,
      "source_reference": null,
      "attachment_url": null,
      "data_source": "nse",
      "source": "nse",
      "fetched_at": "2026-11-02T17:52:23Z",
      "demo_mode": false,
      "rank_score": 30.41,
      "rank_reasons": [
        "Source materiality 0/10",
        "Category significance 1/9",
        "Company is marked in the portfolio",
        "Recency 9.41/10",
        "Supporting details available"
      ],
      "collapsed_count": 3,
      "supporting_details": {
        "grouped_events": [
          {
            "id": "announcement:c9b04f7dd5b93c2d084e724855bcce7709f3c7dd680990f6e7505f0c46dc868c",
            "headline": "Outcome of Board Meeting",
            "occurred_at": "2026-10-29T10:21:45Z",
            "source_reference": "106834353",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/SUZLON1_29102026154942_Suzlon29102026.pdf"
          },
          {
            "id": "announcement:e39df7d359ebe09249613d8c9044d5dc3a86548878fb3908dabf0097d2ea0f52",
            "headline": "ESOP/ESOS/ESPS",
            "occurred_at": "2026-10-21T10:37:30Z",
            "source_reference": "106823458",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/SUZLON1_21102026160631_Suzlon21102026.pdf"
          },
          {
            "id": "announcement:1bf2ac6c714a6e65172b41ca271718395da55e96056ec2685723618fee34a105",
            "headline": "Certificate under SEBI (Depositories and Participants) Regulations, 2018",
            "occurred_at": "2026-10-09T09:22:12Z",
            "source_reference": "106812495",
            "attachment_url": "https://nsearchives.nseindia.com/corporate/SUZLON1_09102026145146_Certificate_74_5_.pdf"
          }
        ]
      }
    }
  ],
  "collapsed_count": 226,
  "total_count": 45,
  "limit": 50,
  "offset": 0,
  "sort": "relevance"
};

export const FALLBACK_ALERTS: AlertsResponse = {
  "as_of": "2026-11-03T17:57:20.960490Z",
  "demo_mode": false,
  "alerts": [
    {
      "id": "alert:price:HDFCBANK:2026-11-03",
      "kind": "price",
      "alert_type": "price_move",
      "ticker": "HDFCBANK",
      "title": "HDFCBANK Price Move",
      "reason": "price +3.6%",
      "message": "price +3.6%",
      "triggered_at": "2026-11-03T00:00:00Z",
      "source": "yfinance",
      "read": false
    },
    {
      "id": "alert:price:HINDUNILVR:2026-11-03",
      "kind": "price",
      "alert_type": "price_move",
      "ticker": "HINDUNILVR",
      "title": "HINDUNILVR Price Move",
      "reason": "price +3.4%",
      "message": "price +3.4%",
      "triggered_at": "2026-11-03T00:00:00Z",
      "source": "yfinance",
      "read": false
    },
    {
      "id": "alert:volume:RELIANCE:2026-11-03",
      "kind": "volume",
      "alert_type": "volume_spike",
      "ticker": "RELIANCE",
      "title": "RELIANCE Volume Spike",
      "reason": "Volume 2.3x its 20-day average",
      "message": "Volume 2.3x its 20-day average",
      "triggered_at": "2026-11-03T00:00:00Z",
      "source": "yfinance",
      "read": false
    },
    {
      "id": "alert:volume:SBIN:2026-11-03",
      "kind": "volume",
      "alert_type": "volume_spike",
      "ticker": "SBIN",
      "title": "SBIN Volume Spike",
      "reason": "Volume 3.1x its 20-day average",
      "message": "Volume 3.1x its 20-day average",
      "triggered_at": "2026-11-03T00:00:00Z",
      "source": "yfinance",
      "read": false
    }
  ]
};

export const FALLBACK_ANOMALIES: AnomaliesResponse = {
  "as_of": "2026-11-03T00:00:00Z",
  "demo_mode": false,
  "data_source": "yfinance",
  "anomalies": [
    {
      "id": "price-anomaly:HDFCBANK:2026-11-03:price_move",
      "ticker": "HDFCBANK",
      "anomaly_type": "price_move",
      "observed_value": 3.6428571428571477,
      "threshold_value": 3.0,
      "unit": "percent",
      "detected_at": "2026-11-03T00:00:00",
      "explanation": "price +3.6%"
    },
    {
      "id": "price-anomaly:HINDUNILVR:2026-11-03:price_move",
      "ticker": "HINDUNILVR",
      "anomaly_type": "price_move",
      "observed_value": 3.3977768709334333,
      "threshold_value": 3.0,
      "unit": "percent",
      "detected_at": "2026-11-03T00:00:00",
      "explanation": "price +3.4%"
    },
    {
      "id": "price-anomaly:RELIANCE:2026-11-03:volume_spike",
      "ticker": "RELIANCE",
      "anomaly_type": "volume_spike",
      "observed_value": 2.26652220228089,
      "threshold_value": 2.0,
      "unit": "multiple",
      "detected_at": "2026-11-03T00:00:00",
      "explanation": "Volume 2.3x its 20-day average"
    },
    {
      "id": "price-anomaly:SBIN:2026-11-03:volume_spike",
      "ticker": "SBIN",
      "anomaly_type": "volume_spike",
      "observed_value": 3.0791365974548848,
      "threshold_value": 2.0,
      "unit": "multiple",
      "detected_at": "2026-11-03T00:00:00",
      "explanation": "Volume 3.1x its 20-day average"
    }
  ]
};

export const FALLBACK_RESULTS_FILINGS: ResultsFilingsResponse = {
  "count": 0,
  "demo_mode": false,
  "filings": []
};

export const FALLBACK_RESEARCH_MODULES: { modules: ResearchModuleInfo[]; count: number } = {
  "modules": [
    {
      "id": "business_snapshot",
      "title": "Business Snapshot",
      "description": "Core operating segments, geographical exposure, competitive moats, and business model.",
      "icon": "\ud83c\udfe2",
      "category": "Strategic"
    },
    {
      "id": "financial_snapshot",
      "title": "Financial Snapshot",
      "description": "Reported scale, margin corridors, EBITDA generation, return ratios, and revenue composition.",
      "icon": "\ud83d\udcca",
      "category": "Financial"
    },
    {
      "id": "trajectory",
      "title": "Growth Trajectory",
      "description": "Multi-year CAGR, organic growth trends, operational momentum, and cyclical inflection points.",
      "icon": "\ud83d\udcc8",
      "category": "Strategic"
    },
    {
      "id": "balance_sheet",
      "title": "Balance Sheet & Solvency",
      "description": "Capital structure, net debt position, working capital cycle, and asset health.",
      "icon": "\ud83c\udfdb",
      "category": "Risk & Solvency"
    },
    {
      "id": "cash_quality",
      "title": "Cash Flow Quality",
      "description": "Operating cash flow conversion ratio, free cash flow conversion, and capex discipline.",
      "icon": "\ud83d\udca7",
      "category": "Financial"
    },
    {
      "id": "narrative_vs_numbers",
      "title": "Narrative vs. Numbers",
      "description": "Audited reconciliation comparing management concall statements against actual balance sheet results.",
      "icon": "\u2696",
      "category": "Governance"
    },
    {
      "id": "guidance",
      "title": "Guidance & Outlook",
      "description": "Executive guidance bands, target visibility, demand commentary, and pipeline milestones.",
      "icon": "\ud83c\udfaf",
      "category": "Forward-Looking"
    },
    {
      "id": "bull_vs_bear",
      "title": "Bull vs. Bear Thesis",
      "description": "Balanced, citation-verified bull catalysts vs structural headwinds and operational risks.",
      "icon": "\ud83d\udc02\ud83d\udc3b",
      "category": "Investment Thesis"
    }
  ],
  "count": 8
};

export const FALLBACK_COMMITMENTS_INFY: CompanyCommitmentsResponse = {
  "ticker": "INFY",
  "company_name": "Infosys Limited",
  "track_record": {
    "total_commitments": 4,
    "delivered_count": 3,
    "beat_count": 2,
    "met_count": 1,
    "missed_count": 1,
    "in_progress_count": 0,
    "delivery_score_pct": 75.0,
    "category_breakdown": {
      "operational": {
        "total": 1,
        "beat": 1,
        "met": 0,
        "missed": 0,
        "in_progress": 0,
        "delivery_score_pct": 100.0
      },
      "revenue_growth": {
        "total": 1,
        "beat": 0,
        "met": 0,
        "missed": 1,
        "in_progress": 0,
        "delivery_score_pct": 0.0
      },
      "margin": {
        "total": 1,
        "beat": 0,
        "met": 1,
        "missed": 0,
        "in_progress": 0,
        "delivery_score_pct": 100.0
      },
      "capital_allocation": {
        "total": 1,
        "beat": 1,
        "met": 0,
        "missed": 0,
        "in_progress": 0,
        "delivery_score_pct": 100.0
      }
    }
  },
  "count": 4,
  "commitments": [
    {
      "id": "promise:INFY:genai-training",
      "ticker": "INFY",
      "category": "operational",
      "promise_headline": "Enterprise Generative AI Workforce Training of 100,000+ Engineers on Topaz",
      "promised_by": "Salil Parekh, CEO & Managing Director",
      "promised_at": "2023-07-20T16:30:00Z",
      "promised_period": "FY24\u2013FY25",
      "promised_document": "Infosys Q1 FY24 Earnings Press Release & Concall",
      "promised_quote": "We have launched Infosys Topaz and committed to training over 100,000 employees in generative AI capabilities.",
      "promised_locator": "Page 2, Technology & Innovation Focus",
      "target_metric": "100,000 Trained Employees",
      "target_date": "2024-09-30",
      "status": "beat",
      "delivered_at": "2024-10-17T16:00:00Z",
      "delivered_document": "Infosys Q2 FY25 Media and Analyst Briefing",
      "delivered_quote": "Over 130,000 employees have now been certified in Generative AI technologies and prompt engineering.",
      "delivered_locator": "Page 4, Strategy Update",
      "delivered_metric": "130,000+ Certified Engineers",
      "variance_pct": 30.0,
      "delivery_assessment": "Surpassed original headcount training target by 30% through mandatory Lex platform learning pathways.",
      "management_explanation": "Rapid adoption of internal GenAI assistants and developer accelerators boosted engineering participation.",
      "source": "primary_filing",
      "source_url": "https://www.infosys.com/investors/reports/financial/quarterly/2024-2025/q2.html",
      "demo_mode": true
    },
    {
      "id": "promise:INFY:fy24-growth-guidance",
      "ticker": "INFY",
      "category": "revenue_growth",
      "promise_headline": "FY24 Constant Currency Revenue Growth Guidance of 4.0% \u2013 7.0%",
      "promised_by": "Salil Parekh, CEO & Managing Director",
      "promised_at": "2023-04-13T16:00:00Z",
      "promised_period": "FY24",
      "promised_document": "Infosys Q4 FY23 Earnings Conference Call Transcript",
      "promised_quote": "For the fiscal year 2024, our revenue growth guidance is 4% to 7% in constant currency terms.",
      "promised_locator": "Page 3, Management Remarks",
      "target_metric": "4.0% \u2013 7.0% CC Growth",
      "target_date": "2024-03-31",
      "status": "missed",
      "delivered_at": "2024-04-18T16:00:00Z",
      "delivered_document": "Infosys Q4 FY24 Audited Financial Results and Press Release",
      "delivered_quote": "FY24 revenue growth was 1.9% in constant currency, impacted by slowdown in discretionary spending.",
      "delivered_locator": "Page 1, Press Release Headline Metrics",
      "delivered_metric": "1.9% CC Growth",
      "variance_pct": -2.1,
      "delivery_assessment": "Missed lower boundary of original guidance by 2.1 percentage points as macro headwinds delayed enterprise client digital transformations in US & European BFSI.",
      "management_explanation": "Clients reprioritized budgets from discretionary digital transformation toward cost optimization and vendor consolidation.",
      "source": "primary_filing",
      "source_url": "https://www.infosys.com/investors/reports/financial/quarterly/2023-2024/q4.html",
      "demo_mode": true
    },
    {
      "id": "promise:INFY:fy24-margin-band",
      "ticker": "INFY",
      "category": "margin",
      "promise_headline": "Operating Margin Guidance Band of 20.0% \u2013 22.0% for FY24",
      "promised_by": "Nilanjan Roy, Former Chief Financial Officer",
      "promised_at": "2023-04-13T16:00:00Z",
      "promised_period": "FY24",
      "promised_document": "Infosys Q4 FY23 Financial Analyst Presentation",
      "promised_quote": "Operating margin for the fiscal year 2024 is expected to be in the range of 20% to 22%.",
      "promised_locator": "Slide 14, Guidance Outlook",
      "target_metric": "20.0% \u2013 22.0% EBIT Margin",
      "target_date": "2024-03-31",
      "status": "met",
      "delivered_at": "2024-04-18T16:00:00Z",
      "delivered_document": "Infosys FY24 Annual Audited Standalone and Consolidated Results",
      "delivered_quote": "Operating margin for the full year FY24 stood at 20.6%, within our stated guidance band.",
      "delivered_locator": "Page 2, Consolidated Financial Highlights",
      "delivered_metric": "20.6% EBIT Margin",
      "variance_pct": 0.0,
      "delivery_assessment": "Delivered solidly inside the guided 20-22% margin corridor through Project Maximus cost optimization and disciplined pyramid rationalization.",
      "management_explanation": "Efficiency gains in sub-contractor rationalization and utilization improvements helped offset wage increments and macro pricing pressure.",
      "source": "primary_filing",
      "source_url": "https://www.infosys.com/investors/reports/financial/quarterly/2023-2024/q4.html",
      "demo_mode": true
    },
    {
      "id": "promise:INFY:capital-allocation-fcf",
      "ticker": "INFY",
      "category": "capital_allocation",
      "promise_headline": "Commitment to Return 85% of Cumulative Free Cash Flow Over 5-Year Cycle",
      "promised_by": "Board of Directors, Infosys Limited",
      "promised_at": "2019-07-12T10:00:00Z",
      "promised_period": "FY20\u2013FY24 Cycle",
      "promised_document": "Infosys Capital Allocation Policy Announcement",
      "promised_quote": "The Board has decided to increase the capital return payout to approximately 85% of cumulative free cash flow over a 5-year period starting FY20.",
      "promised_locator": "Exchange Disclosure Announcement Ref No. 43/2019",
      "target_metric": "\u2265 85.0% FCF Payout",
      "target_date": "2024-03-31",
      "status": "beat",
      "delivered_at": "2024-04-18T16:00:00Z",
      "delivered_document": "Infosys Annual Report FY24 \u2014 Financial Review",
      "delivered_quote": "Cumulative capital return to shareholders across FY20-FY24 totaled ~86% of free cash flow via regular dividends and share buybacks.",
      "delivered_locator": "Page 48, Capital Return to Shareholders",
      "delivered_metric": "86.0% Cumulative FCF Returned",
      "variance_pct": 1.0,
      "delivery_assessment": "Exceeded stated capital return policy target by returning \u20b986,000+ Cr to shareholders across the 5-year window.",
      "management_explanation": "Consistent cash flow conversion supported generous dividend payouts along with completed open-market share buybacks.",
      "source": "primary_filing",
      "source_url": "https://www.infosys.com/investors/reports/annual-report/2023-2024.html",
      "demo_mode": true
    }
  ],
  "as_of": "2026-11-03T17:57:21.039758Z",
  "demo_mode": true
};

export const FALLBACK_COMMITMENTS_SUMMARY_INFY: CommitmentSummaryResponse = {
  "ticker": "INFY",
  "company_name": "Infosys Limited",
  "delivery_score_pct": 75.0,
  "total_commitments": 4,
  "beat_count": 2,
  "met_count": 1,
  "missed_count": 1,
  "in_progress_count": 0,
  "as_of": "2026-11-03T17:57:21.055645Z",
  "demo_mode": true
};

export const FALLBACK_FUNDAMENTALS_INFY: FundamentalsOverview = {
  "ticker": "INFY",
  "company_name": "Infosys Limited",
  "sector": "IT Services",
  "industry": "IT Services & Consulting",
  "basis": "consolidated",
  "market_cap_inr_cr": 474566.8,
  "current_price": 1148.0999755859375,
  "pe_ratio": 15.23,
  "pb_ratio": 4.77,
  "roe_pct": 32.52,
  "roce_pct": 42.34,
  "dividend_yield_pct": 1.25,
  "latest_quarter": {
    "id": "INFY:consolidated:quarterly:2026-09-30",
    "ticker": "INFY",
    "basis": "consolidated",
    "period_type": "quarterly",
    "period_end": "2026-09-30",
    "period_label": "Q2 FY27",
    "fiscal_year": 2027,
    "fiscal_quarter": 2,
    "revenue": 45850.0,
    "other_income": 1320.0,
    "total_expenses": 35900.0,
    "operating_profit": 9950.0,
    "ebitda": 11870.0,
    "depreciation": 1310.0,
    "finance_costs": 138.0,
    "pbt": 11142.0,
    "tax": 2862.0,
    "pat": 8280.0,
    "eps": 20.0,
    "total_assets": 165400.0,
    "total_equity": 104200.0,
    "total_borrowings": 10100.0,
    "cash_and_equivalents": 21900.0,
    "net_debt": -11800.0,
    "cash_from_operations": 8550.0,
    "capex": 760.0,
    "free_cash_flow": 7790.0,
    "operating_margin_pct": 21.7,
    "ebitda_margin_pct": 25.89,
    "net_profit_margin_pct": 18.06,
    "roe_pct": 31.78,
    "roce_pct": 42.35,
    "currency": "INR",
    "unit": "INR Crore",
    "source": "screener",
    "source_url": "https://www.screener.in/company/INFY/consolidated/",
    "is_calculated": {
      "operating_profit": false,
      "ebitda": false,
      "net_debt": false,
      "free_cash_flow": false,
      "operating_margin_pct": false,
      "ebitda_margin_pct": false,
      "net_profit_margin_pct": false,
      "roe_pct": false,
      "roce_pct": false
    }
  },
  "latest_annual": {
    "id": "INFY:consolidated:annual:2026-03-31",
    "ticker": "INFY",
    "basis": "consolidated",
    "period_type": "annual",
    "period_end": "2026-03-31",
    "period_label": "FY26",
    "fiscal_year": 2026,
    "fiscal_quarter": null,
    "revenue": 174400.0,
    "other_income": 4820.0,
    "total_expenses": 136800.0,
    "operating_profit": 37600.0,
    "ebitda": 44580.0,
    "depreciation": 4960.0,
    "finance_costs": 510.0,
    "pbt": 41910.0,
    "tax": 10750.0,
    "pat": 31160.0,
    "eps": 75.4,
    "total_assets": 159200.0,
    "total_equity": 99400.0,
    "total_borrowings": 9800.0,
    "cash_and_equivalents": 20400.0,
    "net_debt": -10600.0,
    "cash_from_operations": 30200.0,
    "capex": 2800.0,
    "free_cash_flow": 27400.0,
    "operating_margin_pct": 21.56,
    "ebitda_margin_pct": 25.56,
    "net_profit_margin_pct": 17.87,
    "roe_pct": 32.52,
    "roce_pct": 42.34,
    "currency": "INR",
    "unit": "INR Crore",
    "source": "screener",
    "source_url": "https://www.screener.in/company/INFY/consolidated/",
    "is_calculated": {
      "operating_profit": false,
      "ebitda": false,
      "net_debt": false,
      "free_cash_flow": false,
      "operating_margin_pct": false,
      "ebitda_margin_pct": false,
      "net_profit_margin_pct": false,
      "roe_pct": false,
      "roce_pct": false
    }
  },
  "as_of": "2026-11-03T17:57:21.070484Z",
  "demo_mode": true,
  "source": "screener"
};

export const FALLBACK_FUNDAMENTALS_HISTORY_INFY: FundamentalsHistoryResponse = {
  "ticker": "INFY",
  "company_name": "Infosys Limited",
  "basis": "consolidated",
  "period_type": "annual",
  "count": 4,
  "as_of": "2026-11-03T17:57:21.085996Z",
  "demo_mode": true,
  "periods": [
    {
      "id": "INFY:consolidated:annual:2023-03-31",
      "ticker": "INFY",
      "basis": "consolidated",
      "period_type": "annual",
      "period_end": "2023-03-31",
      "period_label": "FY23",
      "fiscal_year": 2023,
      "fiscal_quarter": null,
      "revenue": 146767.0,
      "other_income": 2701.0,
      "total_expenses": 111581.0,
      "operating_profit": 35186.0,
      "ebitda": 39411.0,
      "depreciation": 4225.0,
      "finance_costs": 284.0,
      "pbt": 33407.0,
      "tax": 9308.0,
      "pat": 24099.0,
      "eps": 57.6,
      "total_assets": 125792.0,
      "total_equity": 75407.0,
      "total_borrowings": 8115.0,
      "cash_and_equivalents": 13958.0,
      "net_debt": -5843.0,
      "cash_from_operations": 23214.0,
      "capex": 2603.0,
      "free_cash_flow": 20611.0,
      "operating_margin_pct": 23.97,
      "ebitda_margin_pct": 26.85,
      "net_profit_margin_pct": 16.42,
      "roe_pct": 31.96,
      "roce_pct": 42.15,
      "currency": "INR",
      "unit": "INR Crore",
      "source": "screener",
      "source_url": "https://www.screener.in/company/INFY/consolidated/",
      "is_calculated": {
        "operating_profit": false,
        "ebitda": false,
        "net_debt": false,
        "free_cash_flow": false,
        "operating_margin_pct": false,
        "ebitda_margin_pct": false,
        "net_profit_margin_pct": false,
        "roe_pct": false,
        "roce_pct": false
      }
    },
    {
      "id": "INFY:consolidated:annual:2024-03-31",
      "ticker": "INFY",
      "basis": "consolidated",
      "period_type": "annual",
      "period_end": "2024-03-31",
      "period_label": "FY24",
      "fiscal_year": 2024,
      "fiscal_quarter": null,
      "revenue": 153670.0,
      "other_income": 4206.0,
      "total_expenses": 121968.0,
      "operating_profit": 31702.0,
      "ebitda": 37920.0,
      "depreciation": 4412.0,
      "finance_costs": 482.0,
      "pbt": 35426.0,
      "tax": 9178.0,
      "pat": 26248.0,
      "eps": 63.4,
      "total_assets": 139122.0,
      "total_equity": 86183.0,
      "total_borrowings": 9132.0,
      "cash_and_equivalents": 16427.0,
      "net_debt": -7295.0,
      "cash_from_operations": 25230.0,
      "capex": 2480.0,
      "free_cash_flow": 22750.0,
      "operating_margin_pct": 20.63,
      "ebitda_margin_pct": 24.68,
      "net_profit_margin_pct": 17.08,
      "roe_pct": 30.46,
      "roce_pct": 40.23,
      "currency": "INR",
      "unit": "INR Crore",
      "source": "screener",
      "source_url": "https://www.screener.in/company/INFY/consolidated/",
      "is_calculated": {
        "operating_profit": false,
        "ebitda": false,
        "net_debt": false,
        "free_cash_flow": false,
        "operating_margin_pct": false,
        "ebitda_margin_pct": false,
        "net_profit_margin_pct": false,
        "roe_pct": false,
        "roce_pct": false
      }
    },
    {
      "id": "INFY:consolidated:annual:2025-03-31",
      "ticker": "INFY",
      "basis": "consolidated",
      "period_type": "annual",
      "period_end": "2025-03-31",
      "period_label": "FY25",
      "fiscal_year": 2025,
      "fiscal_quarter": null,
      "revenue": 162980.0,
      "other_income": 4510.0,
      "total_expenses": 128420.0,
      "operating_profit": 34560.0,
      "ebitda": 41210.0,
      "depreciation": 4720.0,
      "finance_costs": 490.0,
      "pbt": 38350.0,
      "tax": 9920.0,
      "pat": 28430.0,
      "eps": 68.8,
      "total_assets": 148500.0,
      "total_equity": 92300.0,
      "total_borrowings": 9450.0,
      "cash_and_equivalents": 18120.0,
      "net_debt": -8670.0,
      "cash_from_operations": 27850.0,
      "capex": 2650.0,
      "free_cash_flow": 25200.0,
      "operating_margin_pct": 21.21,
      "ebitda_margin_pct": 25.29,
      "net_profit_margin_pct": 17.44,
      "roe_pct": 31.84,
      "roce_pct": 41.52,
      "currency": "INR",
      "unit": "INR Crore",
      "source": "screener",
      "source_url": "https://www.screener.in/company/INFY/consolidated/",
      "is_calculated": {
        "operating_profit": false,
        "ebitda": false,
        "net_debt": false,
        "free_cash_flow": false,
        "operating_margin_pct": false,
        "ebitda_margin_pct": false,
        "net_profit_margin_pct": false,
        "roe_pct": false,
        "roce_pct": false
      }
    },
    {
      "id": "INFY:consolidated:annual:2026-03-31",
      "ticker": "INFY",
      "basis": "consolidated",
      "period_type": "annual",
      "period_end": "2026-03-31",
      "period_label": "FY26",
      "fiscal_year": 2026,
      "fiscal_quarter": null,
      "revenue": 174400.0,
      "other_income": 4820.0,
      "total_expenses": 136800.0,
      "operating_profit": 37600.0,
      "ebitda": 44580.0,
      "depreciation": 4960.0,
      "finance_costs": 510.0,
      "pbt": 41910.0,
      "tax": 10750.0,
      "pat": 31160.0,
      "eps": 75.4,
      "total_assets": 159200.0,
      "total_equity": 99400.0,
      "total_borrowings": 9800.0,
      "cash_and_equivalents": 20400.0,
      "net_debt": -10600.0,
      "cash_from_operations": 30200.0,
      "capex": 2800.0,
      "free_cash_flow": 27400.0,
      "operating_margin_pct": 21.56,
      "ebitda_margin_pct": 25.56,
      "net_profit_margin_pct": 17.87,
      "roe_pct": 32.52,
      "roce_pct": 42.34,
      "currency": "INR",
      "unit": "INR Crore",
      "source": "screener",
      "source_url": "https://www.screener.in/company/INFY/consolidated/",
      "is_calculated": {
        "operating_profit": false,
        "ebitda": false,
        "net_debt": false,
        "free_cash_flow": false,
        "operating_margin_pct": false,
        "ebitda_margin_pct": false,
        "net_profit_margin_pct": false,
        "roe_pct": false,
        "roce_pct": false
      }
    }
  ]
};

export const FALLBACK_FUNDAMENTALS_RATIOS_INFY: FundamentalsRatiosResponse = {
  "ticker": "INFY",
  "company_name": "Infosys Limited",
  "basis": "consolidated",
  "as_of": "2026-11-03T17:57:21.102628Z",
  "demo_mode": true,
  "current_ratios": {
    "operating_margin_pct": 21.7,
    "ebitda_margin_pct": 25.89,
    "net_profit_margin_pct": 18.06,
    "roe_pct": 31.78,
    "roce_pct": 42.35,
    "debt_to_equity": 0.1,
    "interest_coverage": 81.67
  },
  "trends": [
    {
      "period_label": "FY23",
      "period_end": "2023-03-31",
      "operating_margin_pct": 23.97,
      "ebitda_margin_pct": 26.85,
      "net_profit_margin_pct": 16.42,
      "roe_pct": 31.96,
      "roce_pct": 42.15,
      "debt_to_equity": 0.11,
      "interest_coverage": 133.4
    },
    {
      "period_label": "FY24",
      "period_end": "2024-03-31",
      "operating_margin_pct": 20.63,
      "ebitda_margin_pct": 24.68,
      "net_profit_margin_pct": 17.08,
      "roe_pct": 30.46,
      "roce_pct": 40.23,
      "debt_to_equity": 0.11,
      "interest_coverage": 74.5
    },
    {
      "period_label": "FY25",
      "period_end": "2025-03-31",
      "operating_margin_pct": 21.21,
      "ebitda_margin_pct": 25.29,
      "net_profit_margin_pct": 17.44,
      "roe_pct": 31.84,
      "roce_pct": 41.52,
      "debt_to_equity": 0.1,
      "interest_coverage": 79.73
    },
    {
      "period_label": "Q1 FY26",
      "period_end": "2025-06-30",
      "operating_margin_pct": 21.17,
      "ebitda_margin_pct": 25.35,
      "net_profit_margin_pct": 17.68,
      "roe_pct": 30.21,
      "roce_pct": 40.85,
      "debt_to_equity": 0.1,
      "interest_coverage": 77.44
    },
    {
      "period_label": "Q2 FY26",
      "period_end": "2025-09-30",
      "operating_margin_pct": 21.53,
      "ebitda_margin_pct": 25.65,
      "net_profit_margin_pct": 17.92,
      "roe_pct": 31.27,
      "roce_pct": 41.62,
      "debt_to_equity": 0.1,
      "interest_coverage": 79.77
    },
    {
      "period_label": "Q3 FY26",
      "period_end": "2025-12-31",
      "operating_margin_pct": 21.64,
      "ebitda_margin_pct": 25.78,
      "net_profit_margin_pct": 18.01,
      "roe_pct": 31.59,
      "roce_pct": 42.1,
      "debt_to_equity": 0.1,
      "interest_coverage": 80.69
    },
    {
      "period_label": "FY26",
      "period_end": "2026-03-31",
      "operating_margin_pct": 21.56,
      "ebitda_margin_pct": 25.56,
      "net_profit_margin_pct": 17.87,
      "roe_pct": 32.52,
      "roce_pct": 42.34,
      "debt_to_equity": 0.1,
      "interest_coverage": 83.18
    },
    {
      "period_label": "Q4 FY26",
      "period_end": "2026-03-31",
      "operating_margin_pct": 21.61,
      "ebitda_margin_pct": 25.77,
      "net_profit_margin_pct": 17.98,
      "roe_pct": 31.47,
      "roce_pct": 42.05,
      "debt_to_equity": 0.1,
      "interest_coverage": 80.76
    },
    {
      "period_label": "Q1 FY27",
      "period_end": "2026-06-30",
      "operating_margin_pct": 21.62,
      "ebitda_margin_pct": 25.81,
      "net_profit_margin_pct": 18.0,
      "roe_pct": 31.39,
      "roce_pct": 41.98,
      "debt_to_equity": 0.1,
      "interest_coverage": 80.67
    },
    {
      "period_label": "Q2 FY27",
      "period_end": "2026-09-30",
      "operating_margin_pct": 21.7,
      "ebitda_margin_pct": 25.89,
      "net_profit_margin_pct": 18.06,
      "roe_pct": 31.78,
      "roce_pct": 42.35,
      "debt_to_equity": 0.1,
      "interest_coverage": 81.67
    }
  ]
};

export const FALLBACK_ASK_SUGGESTIONS: { ticker: string; suggestions: string[]; count: number } = {
  "ticker": "INFY",
  "suggestions": [
    "What was FY24 revenue and constant currency growth guidance vs actuals?",
    "Did management achieve its GenAI workforce training target of 100,000 engineers?",
    "What is Infosys's capital allocation and Free Cash Flow payout track record?",
    "What are the operating margin corridors and cost optimization drivers?"
  ],
  "count": 4
};

export function getFallbackForPath<T>(path: string): T | null {
  const clean = path.split("?")[0];
  if (clean === "/portfolio") return FALLBACK_PORTFOLIO as unknown as T;
  if (clean === "/digest") {
    if (path.includes("window=7d") || path.includes("window=3d")) {
      return FALLBACK_DIGEST_7D as unknown as T;
    }
    return FALLBACK_DIGEST_24H as unknown as T;
  }
  if (clean === "/alerts") return FALLBACK_ALERTS as unknown as T;
  if (clean === "/anomalies") return FALLBACK_ANOMALIES as unknown as T;
  if (clean === "/results-filings") return FALLBACK_RESULTS_FILINGS as unknown as T;
  if (clean === "/research/modules") return FALLBACK_RESEARCH_MODULES as unknown as T;
  if (clean.startsWith("/commitments/") && clean.endsWith("/summary")) return FALLBACK_COMMITMENTS_SUMMARY_INFY as unknown as T;
  if (clean.startsWith("/commitments/")) return FALLBACK_COMMITMENTS_INFY as unknown as T;
  if (clean.startsWith("/fundamentals/") && clean.endsWith("/history")) return FALLBACK_FUNDAMENTALS_HISTORY_INFY as unknown as T;
  if (clean.startsWith("/fundamentals/") && clean.endsWith("/ratios")) return FALLBACK_FUNDAMENTALS_RATIOS_INFY as unknown as T;
  if (clean.startsWith("/fundamentals/")) return FALLBACK_FUNDAMENTALS_INFY as unknown as T;
  if (clean.startsWith("/ask/suggestions/")) return FALLBACK_ASK_SUGGESTIONS as unknown as T;
  return null;
}
