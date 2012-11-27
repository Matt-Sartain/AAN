MONTH_CHOICES = (
    ('1', 'January'),
    ('2', 'Feburary'),
    ('3', 'March'),
    ('4', 'April'),
    ('5', 'May'),
    ('6', 'June'),
    ('7', 'July'),
    ('8', 'August'),
    ('9', 'September'),
    ('10', 'October'),
    ('11', 'November'),
    ('12', 'December'),
)

ORGTYPE_PUBLISHER = 1
ORGTYPE_ADVERTISER = 2
ORGTYPE_NETWORK = 3


ORGTYPE_CHOICES = ( 
    (ORGTYPE_PUBLISHER, 'Publisher'),
    (ORGTYPE_ADVERTISER, 'Advertiser'),
    (ORGTYPE_NETWORK, 'Network'),
)


ORGFILTER_FEATURED = 1
ORGFILTER_OURPICKS= 2
ORGFILTER_SMARTADS = 3

ORGFILTER_CHOICES = (
    (ORGFILTER_FEATURED, 'Featured'),
    (ORGFILTER_OURPICKS, 'Our Picks'),
    (ORGFILTER_SMARTADS, 'Smart Ads'),
)

RELATIONSHIP_NONE = 0
RELATIONSHIP_INVITED = 1
RELATIONSHIP_APPLIED = 2
RELATIONSHIP_ACCEPTED = 3
RELATIONSHIP_DECLINED = 4
RELATIONSHIP_TERMINATED = 5
RELATIONSHIP_EXPIRED = 6
RELATIONSHIP_RETRACTED = 7

RELATIONSHIP_CHOICES = (
    (RELATIONSHIP_NONE,"None"),
    (RELATIONSHIP_INVITED,"Invited"),
    (RELATIONSHIP_APPLIED,"Applied"),
    (RELATIONSHIP_ACCEPTED,"Accepted"),
    (RELATIONSHIP_DECLINED,"Declined"),
    (RELATIONSHIP_TERMINATED,"Terminated"),
    (RELATIONSHIP_EXPIRED,"Expired"),
    (RELATIONSHIP_RETRACTED,"Retracted"),
)


LINKASSIGNED_ALL = 1
LINKASSIGNED_PROGRAM_TERM = 2
LINKASSIGNED_GROUP = 3
LINKASSIGNED_INDIVIDUAL = 4
LINKASSIGNED_MINIMUM_RATING = 5
LINKASSIGNED_PROMOTION_METHOD = 6
LINKASSIGNED_PUBLISHER_VERTICAL = 7

LINKASSIGNED_CHOICES = (
    (LINKASSIGNED_ALL , 'All'),
    (LINKASSIGNED_PROGRAM_TERM , 'Program Term'),
    (LINKASSIGNED_GROUP , 'Group'),
    (LINKASSIGNED_INDIVIDUAL , 'Individual Publisher'),
    #(LINKASSIGNED_MINIMUM_RATING , 'Minimum Rating'),
    (LINKASSIGNED_PROMOTION_METHOD , 'Promotion Method'),
    (LINKASSIGNED_PUBLISHER_VERTICAL , 'Publisher Defined Vertical'),
    )

LINKTYPE_NONE = 0
LINKTYPE_BANNER = 1
LINKTYPE_TEXT = 2
LINKTYPE_KEYWORD = 3
LINKTYPE_FLASH = 4
LINKTYPE_EMAIL = 5
LINKTYPE_HTML = 6
LINKTYPE_RSS = 7
LINKTYPE_AB = 8

LINKTYPE_CHOICES = (
    (LINKTYPE_NONE , 'None'),
    (LINKTYPE_BANNER , 'Banner'),
    (LINKTYPE_TEXT , 'Text'),
    (LINKTYPE_KEYWORD , 'Keyword'),
    (LINKTYPE_FLASH , 'Flash'),
    (LINKTYPE_EMAIL , 'Email Campaign'),
    (LINKTYPE_HTML , 'HTML'),
    (LINKTYPE_RSS  , 'RSS'),
    (LINKTYPE_AB  , 'Adbuilder'),
    )

DATAFEEDTYPE_NONE = 0
DATAFEEDTYPE_FTPPUSH = 1
DATAFEEDTYPE_FTPPULL = 2
DATAFEEDTYPE_HTTP = 3
DATAFEEDTYPE_EMAIL = 4

DATAFEEDTYPE_CHOICES = (
    (DATAFEEDTYPE_FTPPUSH,'FTP Push'),
    (DATAFEEDTYPE_FTPPULL,'FTP Pull'),
    (DATAFEEDTYPE_HTTP,'HTTP Pull'),
)

PUB_DATAFEEDTYPE_CHOICES = (
    (DATAFEEDTYPE_FTPPUSH,'FTP Push'),
    (DATAFEEDTYPE_FTPPULL,'FTP Pull'),
    (DATAFEEDTYPE_EMAIL,'Email'),
)
     

DATAFEEDFORMAT_NONE = 0
DATAFEEDFORMAT_CSV = 1
DATAFEEDFORMAT_EXCEL = 2
DATAFEEDFORMAT_PIPEDELIM = 3
DATAFEEDFORMAT_TABDELIM = 4
DATAFEEDFORMAT_XML = 5

DATAFEEDFORMAT_CHOICES = (
    (DATAFEEDFORMAT_CSV, 'CSV'),
    (DATAFEEDFORMAT_EXCEL, 'Excel'),
    (DATAFEEDFORMAT_PIPEDELIM, 'Text, pipe-delimited'),
    (DATAFEEDFORMAT_TABDELIM, 'Text, tab-delimited'),
)

PUB_DATAFEEDFORMAT_CHOICES = (
    (DATAFEEDFORMAT_CSV, 'CSV'),
    (DATAFEEDFORMAT_PIPEDELIM, 'Text, pipe-delimited'),
    (DATAFEEDFORMAT_TABDELIM, 'Text, tab-delimited'),
)

TAXTYPE_NONE = 0
TAXTYPE_INDIVIDUAL = 1
TAXTYPE_PARTNERSHIP = 2
TAXTYPE_CORPORATION = 3
TAXTYPE_SOLE_PROPRIETORSHIP = 4
TAXTYPE_OTHER = 5
TAXTYPE_FOREIGN = 6
TAXTYPE_LLC = 7
TAXTYPE_LLP = 8
TAXTYPE_NONPROFIT = 9

TAXTYPE_CHOICES = (
    (TAXTYPE_NONE,'None'),
    (TAXTYPE_INDIVIDUAL,'Individual'),
    (TAXTYPE_PARTNERSHIP,'Partnership'),
    (TAXTYPE_CORPORATION,'Corporation'),
    (TAXTYPE_SOLE_PROPRIETORSHIP,'Sole Proprietorship'),
    (TAXTYPE_OTHER,'Other'),
    (TAXTYPE_FOREIGN,'Foreign'),
    (TAXTYPE_LLC,'LLC'),
    (TAXTYPE_LLP,'LLP'),
    (TAXTYPE_NONPROFIT,'Non-Profit'),
    )
    
W9_STATUS_NOT_RECEIVED = 1    
W9_STATUS_RECEIVED = 2
W9_STATUS_CHOICES= (
    (W9_STATUS_NOT_RECEIVED,'Not Received'),
    (W9_STATUS_RECEIVED,'Received'),
    )

INCENTIVETYPE_NONE = 0
INCENTIVETYPE_TOTALSALES = 1
INCENTIVETYPE_TOTALCOMMISSIONS = 2
INCENTIVETYPE_NUMBERORDERS = 3

INCENTIVETYPE_CHOICES = (
    (INCENTIVETYPE_NONE,'None'),
    (INCENTIVETYPE_TOTALSALES,'Total Sales Amount ($)'),
    (INCENTIVETYPE_TOTALCOMMISSIONS,'Total Commissions ($)'),
    (INCENTIVETYPE_NUMBERORDERS,'Number of Orders or Leads'),
    )

ALERTTIMEPERIOD_NONE = 0
ALERTTIMEPERIOD_DAY = 1
ALERTTIMEPERIOD_WEEK = 2
ALERTTIMEPERIOD_MONTH = 3
ALERTTIMEPERIOD_QUARTER = 4
ALERTTIMEPERIOD_COMPARABLE_MONTH = 5
ALERTTIMEPERIOD_COMPARABLE_QUARTER = 6

ALERTTIMEPERIOD_CHOICES = (
    (ALERTTIMEPERIOD_DAY , 'Day'),
    (ALERTTIMEPERIOD_WEEK , 'Week'),
    (ALERTTIMEPERIOD_MONTH , 'Month'),
    (ALERTTIMEPERIOD_QUARTER , 'Quarter'),
    (ALERTTIMEPERIOD_COMPARABLE_MONTH , 'Comparable Month'),
    (ALERTTIMEPERIOD_COMPARABLE_QUARTER , 'Comparable Quarter'),
    )

METRIC_NONE = 0
METRIC_IMPRESSIONS = 1
METRIC_CLICKS = 2
METRIC_LEADS = 3
METRIC_ORDERS = 4
METRIC_AMOUNT = 5
METRIC_COMMISSION_EARNED = 6

METRIC_CHOICES = (
    (METRIC_IMPRESSIONS , 'Impressions'),
    (METRIC_CLICKS , 'Clicks'),
    (METRIC_LEADS , 'Leads'),
    (METRIC_ORDERS , 'Orders'),
    (METRIC_AMOUNT , 'Amount'),
    (METRIC_COMMISSION_EARNED , 'Commission Earned'),
    )
    
    
PIXEL_TYPE_NONE = 0
PIXEL_TYPE_IMAGE = 1
PIXEL_TYPE_IFRAME = 2
PIXEL_TYPE_SCRIPT = 3

PIXEL_TYPE_CHOICES = (
    (PIXEL_TYPE_IMAGE , 'Image pixel'),
    #(PIXEL_TYPE_IFRAME , 'iFrame pixel'),
    (PIXEL_TYPE_SCRIPT , 'Script pixel'),
    )

AUTODECLINEFIELD_NONE = 0
AUTODECLINEFIELD_COUNTRY = 1
AUTODECLINEFIELD_STATE = 2
AUTODECLINEFIELD_PUBLISHER_ID = 3
AUTODECLINEFIELD_PROMOTION_METHOD = 4
AUTODECLINEFIELD_WEBSITE = 5
AUTODECLINEFIELD_PUBLISHER_VERTICAL = 6

AUTODECLINEFIELD_CHOICES = (
    (AUTODECLINEFIELD_NONE,'None'),
    (AUTODECLINEFIELD_COUNTRY,'Country'),
    (AUTODECLINEFIELD_STATE,'State'),
    (AUTODECLINEFIELD_PUBLISHER_ID,'Publisher ID'),
    (AUTODECLINEFIELD_PROMOTION_METHOD,'Promotion Method'),
    (AUTODECLINEFIELD_PUBLISHER_VERTICAL,'Publisher Defined Vertical'),
    (AUTODECLINEFIELD_WEBSITE,'Website'),
    )
    
CAMPAIGNCRITERIAPERIOD_YESTERDAY = 0
CAMPAIGNCRITERIAPERIOD_PAST_7_DAYS = 1
CAMPAIGNCRITERIAPERIOD_MONTH_TO_DATE = 2
CAMPAIGNCRITERIAPERIOD_QUARTER_TO_DATE = 3
CAMPAIGNCRITERIAPERIOD_PAST_30_DAYS = 4
CAMPAIGNCRITERIAPERIOD_LAST_FULL_MONTH = 5
CAMPAIGNCRITERIAPERIOD_LAST_FULL_QUARTER = 6
CAMPAIGNCRITERIAPERIOD_PAST_365_DAYS = 7
CAMPAIGNCRITERIAPERIOD_LAST_FULL_YEAR = 8

CAMPAIGNCRITERIAPERIOD_CHOICES = (
    (CAMPAIGNCRITERIAPERIOD_YESTERDAY , 'Yesterday'),
    (CAMPAIGNCRITERIAPERIOD_PAST_7_DAYS , 'Past 7 Days'),
    (CAMPAIGNCRITERIAPERIOD_MONTH_TO_DATE , 'Month to Date'),
    (CAMPAIGNCRITERIAPERIOD_QUARTER_TO_DATE , 'Quarter to Date'),
    (CAMPAIGNCRITERIAPERIOD_PAST_30_DAYS , 'Past 30 Days'),
    (CAMPAIGNCRITERIAPERIOD_LAST_FULL_MONTH , 'Last Full Month'),
    (CAMPAIGNCRITERIAPERIOD_LAST_FULL_QUARTER , 'Last Full Quarter'),
    (CAMPAIGNCRITERIAPERIOD_PAST_365_DAYS, 'Past 365 Days'),
    (CAMPAIGNCRITERIAPERIOD_LAST_FULL_YEAR , 'Last Full Year'),
    )

REPORTFORMAT_CSV = 0
REPORTFORMAT_TSV = 1
REPORTFORMAT_EXCEL = 2

REPORTFORMAT_CHOICES= (
        (REPORTFORMAT_CSV, 'CSV'),
        (REPORTFORMAT_TSV, 'TXT'),
        (REPORTFORMAT_EXCEL, 'Excel'),
    )


REPORTGROUPBY_DAY = 0
REPORTGROUPBY_WEEK = 1
REPORTGROUPBY_MONTH = 2
REPORTGROUPBY_QUARTER = 3
REPORTGROUPBY_WEBSITE = 4

REPORTGROUPBY_CHOICES = (
        (REPORTGROUPBY_DAY, 'Day'),
        (REPORTGROUPBY_WEEK, 'Week'),
        (REPORTGROUPBY_MONTH, 'Month'),
        (REPORTGROUPBY_QUARTER, 'Quarter'),
        (REPORTGROUPBY_WEBSITE, 'By Website'),
    )

RUNREPORTBY_ALLPUBLISHERS = 0
RUNREPORTBY_GROUP = 1
RUNREPORTBY_VERTICAL = 2
RUNREPORTBY_PUBLISHER = 3
RUNREPORTBY_CHOICES = (
        (RUNREPORTBY_ALLPUBLISHERS, 'All Publishers'),
        (RUNREPORTBY_GROUP, 'Group'),
        (RUNREPORTBY_VERTICAL, 'Vertical'),
        (RUNREPORTBY_PUBLISHER, 'Publishers'),
    )
                                                                               
REPORTTIMEFRAME_YESTERDAY = 0
REPORTTIMEFRAME_PAST7DAYS = 1
REPORTTIMEFRAME_MONTHTODATE = 2
REPORTTIMEFRAME_QUARTERTODATE = 3
REPORTTIMEFRAME_PAST30DAYS = 4
REPORTTIMEFRAME_LASTFULLMONTH = 5
REPORTTIMEFRAME_LASTFULLQUARTER = 6
REPORTTIMEFRAME_PAST365DAYS = 7
REPORTTIMEFRAME_LASTFULLYEAR = 8
REPORTTIMEFRAME_TODAY = 9
REPORTTIMEFRAME_YEARTODATE = 10

REPORTTIMEFRAME_CHOICES =  (
            ( REPORTTIMEFRAME_TODAY, 'Today'),
            ( REPORTTIMEFRAME_YESTERDAY, 'Yesterday'),
            ( REPORTTIMEFRAME_PAST7DAYS, 'Past 7 Days'),
            ( REPORTTIMEFRAME_MONTHTODATE, 'Month to Date'),
            ( REPORTTIMEFRAME_QUARTERTODATE, 'Quarter to Date'),
            ( REPORTTIMEFRAME_PAST30DAYS, 'Past 30 Days'),
            ( REPORTTIMEFRAME_LASTFULLMONTH, 'Last Full Month'),
            ( REPORTTIMEFRAME_LASTFULLQUARTER, 'Last Full Quarter'),
            ( REPORTTIMEFRAME_PAST365DAYS, 'Past 365 Days'),
            ( REPORTTIMEFRAME_LASTFULLYEAR, 'Last Full Year'),
    )




REPORTTYPE_SALES = 0
REPORTTYPE_SALES_BY_PUBLISHER = 1
REPORTTYPE_REVENUE = 2
REPORTTYPE_REVENUE_BY_PUBLISHER =3
REPORTTYPE_CREATIVE = 4
REPORTTYPE_CREATIVE_BY_PROMO = 5
REPORTTYPE_PRODUCT_DETAIL = 6
REPORTTYPE_ORDER_DETAIL = 7
REPORTTYPE_ACCOUNTING = 8
REPORTTYPE_SALES_BY_ADVERTISER = 9
REPORTTYPE_REVENUE_BY_ADVERTISER = 10
REPORTTYPE_DATATRANSFER_ORDERREPORT = 11


REPORTTYPE_CHOICES = (
    (REPORTTYPE_SALES,'Sales and Activity Report'),
    (REPORTTYPE_SALES_BY_PUBLISHER,'Sales and Activity Report by Publisher'),
    (REPORTTYPE_REVENUE,'Revenue Report'),
    (REPORTTYPE_REVENUE_BY_PUBLISHER,'Revenue Report by Publisher'),
    (REPORTTYPE_CREATIVE,'Link Report'),
    (REPORTTYPE_CREATIVE_BY_PROMO,'Link Report by Promo Type'),
    (REPORTTYPE_PRODUCT_DETAIL,'Product Detail Report'),
    (REPORTTYPE_ORDER_DETAIL,'Order Detail Report'),
    (REPORTTYPE_ACCOUNTING,'Accounting Report'),
    )    


REPORTTYPE_CHOICES_PUBLISHER = (
    (REPORTTYPE_SALES,'Sales and Activity Report'),
    (REPORTTYPE_SALES_BY_ADVERTISER,'Sales and Activity Report by Advertiser'),
    (REPORTTYPE_REVENUE,'Revenue Report'),
    (REPORTTYPE_REVENUE_BY_ADVERTISER,'Revenue Report by Advertiser'),
    (REPORTTYPE_CREATIVE,'Link Report'),
    (REPORTTYPE_ORDER_DETAIL,'Order Detail Report'),
    (REPORTTYPE_ACCOUNTING,'Accounting Report'),
    #(REPORTTYPE_DATATRANSFER_ORDERREPORT,'Data Transfer Report'),
    )    


PAYMENT_CHECK = 1
PAYMENT_DEPOSIT = 2
PAYMENT_PAYPAL = 3

PAYMENT_CHOICES = (
    (PAYMENT_CHECK, 'Check'),
    (PAYMENT_DEPOSIT, 'Direct Deposit'),
    (PAYMENT_PAYPAL, 'PayPal'),
)


SMARTADTYPE_PRODUCT = 1
SMARTADTYPE_BANNER = 2

SMARTADTYPE_CHOICES = (
    (SMARTADTYPE_PRODUCT, 'Product'),
    (SMARTADTYPE_BANNER, 'Banner'),
)

INQUIRYSTATUS_UNRESOLVED = 1
INQUIRYSTATUS_RESOLVED = 2
INQUIRYSTATUS_CLOSED = 3

INQUIRYSTATUS_CHOICES = (
    (INQUIRYSTATUS_UNRESOLVED, 'Unresolved'),
    (INQUIRYSTATUS_RESOLVED, 'Resolved'),
    (INQUIRYSTATUS_CLOSED, 'Closed'),
)


ADMINLEVEL_NONE = 0
ADMINLEVEL_ACCOUNT_MANAGER_SECONDARY_ACCOUNT = 1
ADMINLEVEL_ACCOUNT_MANAGER_PRIMARY_ACCOUNT = 2
ADMINLEVEL_AFFILIATE_MANAGER = 3
ADMINLEVEL_AFFILIATE_DIRECTOR = 4
ADMINLEVEL_ADMINISTRATOR = 5

ADMINLEVEL_CHOICES = (
     (ADMINLEVEL_NONE,'None'),
     (ADMINLEVEL_ACCOUNT_MANAGER_SECONDARY_ACCOUNT,'Advertiser Account Manager - Secondary Account'),
     (ADMINLEVEL_ACCOUNT_MANAGER_PRIMARY_ACCOUNT,'Advertiser Account Manager - Primary Account'),
     (ADMINLEVEL_AFFILIATE_MANAGER,'Affiliate Manager'),
     (ADMINLEVEL_AFFILIATE_DIRECTOR,'Affilate Director'),
     (ADMINLEVEL_ADMINISTRATOR,'Administrator'),
     
    )

ORGSTATUS_UNAPPROVED = 1
ORGSTATUS_TEST = 2
ORGSTATUS_LIVE = 3
ORGSTATUS_DEACTIVATED = 4
ORGSTATUS_CLOSED = 5

ORGSTATUS_CHOICES = (
    (ORGSTATUS_UNAPPROVED,'Unapproved'),
    (ORGSTATUS_TEST,'Test'),
    (ORGSTATUS_LIVE,'Live'),
    (ORGSTATUS_DEACTIVATED,'Deactivated'),
    (ORGSTATUS_CLOSED,'Closed'),
    
    )

PUBORGSTATUS_UNAPPROVED = ORGSTATUS_UNAPPROVED
PUBORGSTATUS_ACTIVE = ORGSTATUS_LIVE
PUBORGSTATUS_INREVIEW = ORGSTATUS_UNAPPROVED
PUBORGSTATUS_DISABLED = ORGSTATUS_DEACTIVATED

PUBORGSTATUS_CHOICES = (
    (PUBORGSTATUS_UNAPPROVED,'Unapproved'),
    (PUBORGSTATUS_ACTIVE,'Active'),
    (PUBORGSTATUS_INREVIEW,'In Review'),
    (PUBORGSTATUS_DISABLED,'Disabled'),
    )

STATUS_PENDING = 0
STATUS_TEST = 1
STATUS_LIVE = 2
STATUS_PAUSED = 3
STATUS_DEACTIVATED = 4

STATUS_CHOICES = (
    (STATUS_PENDING,'Pending Approval'),
    (STATUS_TEST,'Test'),
    (STATUS_LIVE,'Live'),
    (STATUS_PAUSED,'Paused'),
    (STATUS_DEACTIVATED,'Deactivated'),
    )
    

LOGSTATE_NEEDS_GRAB = 1
LOGSTATE_NEEDS_PROCESSING = 2
LOGSTATE_DONE = 3

LOGSTATE_CHOICES = (
    (LOGSTATE_NEEDS_GRAB,'Needs Grab'),
    (LOGSTATE_NEEDS_PROCESSING,'Needs Processing'),
    (LOGSTATE_DONE,'Processed'),
    )

ADVERTISERTYPE_SELFMANAGED = 1
ADVERTISERTYPE_MANAGED = 2
ADVERTISERTYPE_CPA = 3

ADVERTISERTYPE_CHOICES = (
    (ADVERTISERTYPE_SELFMANAGED,'Self Managed'),
    (ADVERTISERTYPE_MANAGED,'Managed'),
    (ADVERTISERTYPE_CPA,'CPA'),

    )

TEAM_INHOUSE = 1
TEAM_OUTSOURCE = 2

TEAM_CHOICES = (
    (TEAM_INHOUSE,'In-house'),
    (TEAM_OUTSOURCE,'Outsourced')
    )


AGENCY_INHOUSE = 1
AGENCY_AGENCY = 2

AGENCY_CHOICES = (
    (AGENCY_AGENCY,'Agency'),
    (AGENCY_INHOUSE,'In-house')
    )

EMAILTYPE_ADVERTISER_MESSAGE = 1

DASHBOARDVIEWING_ALL = 1
DASHBOARDVIEWING_PUBLISHERTYPE = 2
DASHBOARDVIEWING_VERTICAL = 3
DASHBOARDVIEWING_GROUP = 4
DASHBOARDVIEWING_PROGRAMTYPE = 5 # flat fee or commission
DASHBOARDVIEWING_SMARTADS_ONLY = 6

DASHBOARDVIEWING_CHOICES = (
    (DASHBOARDVIEWING_ALL,'All'),
    (DASHBOARDVIEWING_PUBLISHERTYPE,'Publisher Type'),
    (DASHBOARDVIEWING_VERTICAL,'Vertical'),
    (DASHBOARDVIEWING_GROUP,'Group'),
    (DASHBOARDVIEWING_PROGRAMTYPE,'Program Type'),
    (DASHBOARDVIEWING_SMARTADS_ONLY,'SmartADs Only'),)

DASHBOARDVIEWINGPROGRAMTYPE_ALL = 1
DASHBOARDVIEWINGPROGRAMTYPE_FLATFEE = 2
DASHBOARDVIEWINGPROGRAMTYPE_COMMISSION = 3
DASHBOARDVIEWINGPROGRAMTYPE_SMARTADS_ONLY = 4

DASHBOARDVIEWINGPROGRAMTYPE_CHOICES = (
    (DASHBOARDVIEWINGPROGRAMTYPE_ALL, 'All Advertisers'),
    (DASHBOARDVIEWINGPROGRAMTYPE_FLATFEE, 'Program Type: Flat Fee'),
    (DASHBOARDVIEWINGPROGRAMTYPE_COMMISSION, 'Program Type: Commission %'),
    (DASHBOARDVIEWINGPROGRAMTYPE_SMARTADS_ONLY, 'Advertisers with SmartAds Only'),
)
    

DASHBOARDMETRIC_NONE = 0
DASHBOARDMETRIC_IMPRESSIONS = 1
DASHBOARDMETRIC_CLICKS = 2
DASHBOARDMETRIC_LEADS = 3
DASHBOARDMETRIC_ORDERS = 4
DASHBOARDMETRIC_SALES = 5
DASHBOARDMETRIC_COMMISSION_EARNED = 6

DASHBOARDMETRIC_CHOICES = (
    (DASHBOARDMETRIC_IMPRESSIONS , 'Impressions'),
    (DASHBOARDMETRIC_CLICKS , 'Clicks'),
    (DASHBOARDMETRIC_LEADS , 'Leads'),
    (DASHBOARDMETRIC_ORDERS , 'Orders'),
    (DASHBOARDMETRIC_SALES , 'Sales'),
    (DASHBOARDMETRIC_COMMISSION_EARNED , 'Commission Earned'),
    )

DASHBOARDMETRIC_CHOICES_PUBLISHER = (
    (DASHBOARDMETRIC_IMPRESSIONS , 'Impressions'),
    (DASHBOARDMETRIC_CLICKS , 'Clicks'),
    (DASHBOARDMETRIC_LEADS , 'Leads'),
    (DASHBOARDMETRIC_ORDERS , 'Orders'),
    (DASHBOARDMETRIC_SALES , 'Sales'),
    (DASHBOARDMETRIC_COMMISSION_EARNED , 'Commission Earned'),
    )

NEWSSTATUS_DRAFT = 0
NEWSSTATUS_LIVE = 1
NEWSSTATUS_EXPIRED = 2

NEWSSTATUS_CHOICES = (
    (NEWSSTATUS_DRAFT, 'Draft'),
    (NEWSSTATUS_LIVE, 'Live'),
    (NEWSSTATUS_EXPIRED, 'Expired'),
)

NEWS_VIEWED_BY_ADV = 0
NEWS_VIEWED_BY_PUB = 1
NEWS_VIEWED_BY_BOTH = 2

NEWS_VIEWED_BY_CHOICES = (
    (NEWS_VIEWED_BY_ADV, 'Advertiser'),
    (NEWS_VIEWED_BY_PUB, 'Publisher'),
    (NEWS_VIEWED_BY_BOTH, 'Adv & Pub'),
)

ADVERTISER_PAYOUT_TYPE_REVSHARE = 4
ADVERTISER_PAYOUT_TYPE_CPA = 1
ADVERTISER_PAYOUT_TYPE_CPC = 5
ADVERTISER_PAYOUT_TYPE_CPM = 12
ADVERTISER_PAYOUT_TYPE_PAYOUTSHARE = 43

ADVERTISER_PAYOUT_TYPE_CHOICES = (
    (ADVERTISER_PAYOUT_TYPE_REVSHARE,'Rev-share'),
    (ADVERTISER_PAYOUT_TYPE_CPA,'CPA'),
    (ADVERTISER_PAYOUT_TYPE_CPC,'CPC'),
    (ADVERTISER_PAYOUT_TYPE_CPM,'CPM'),
    (ADVERTISER_PAYOUT_TYPE_PAYOUTSHARE,'Payout-share'),
    )

TRANSACTION_FEE_TYPE_REVSHARE = 7
TRANSACTION_FEE_TYPE_FLAT = 8
TRANSACTION_FEE_TYPE_PAYOUTSHARE = 9

TRANSACTION_FEE_TYPE_CHOICES = (
    (TRANSACTION_FEE_TYPE_REVSHARE,'Rev-share'),
    (TRANSACTION_FEE_TYPE_FLAT,'Flat'),
    (TRANSACTION_FEE_TYPE_PAYOUTSHARE,'Payout-share'),
    )

PUBLISHER_PAYOUT_TYPE_REVSHARE = 1
PUBLISHER_PAYOUT_TYPE_CPA = 2
PUBLISHER_PAYOUT_TYPE_CPC = 3
PUBLISHER_PAYOUT_TYPE_CPM = 4

PUBLISHER_PAYOUT_TYPE_CHOICES = (
    (PUBLISHER_PAYOUT_TYPE_REVSHARE,'Rev-share'),
    (PUBLISHER_PAYOUT_TYPE_CPA,'CPA'),
    (PUBLISHER_PAYOUT_TYPE_CPC,'CPC'),
    (PUBLISHER_PAYOUT_TYPE_CPM,'CPM'),
    )
    
PENDING_SUBMISSION_SALES_APPROVAL = 0
PENDING_SALES_APPROVAL = 1
APPROVED_BY_SALES_MANAGER = 2
REJECTED_BY_SALES_MANAGER = 3
SENT_PDF_FOR_SIGNATURE = 4
SENT_RECVD_CONTRACT = 5
APPROVED_BY_CREDIT_MANAGER = 6
REJECTED_BY_CREDIT_MANAGER = 7
ALL_SIGNATURE_APPROVAL_RECVD = 8
IO_ACTIVE = 9
IO_COMPLETE = 10

IO_STATUS_TYPE_CHOICES = (
    (PENDING_SUBMISSION_SALES_APPROVAL, 'Pending Submission for Sales Approval'),
    (PENDING_SALES_APPROVAL, 'Pending Sales Approval'),
    (APPROVED_BY_SALES_MANAGER, 'Approved by Sales Manager'),
    (REJECTED_BY_SALES_MANAGER, 'Rejected by Sales Manager'),
    (SENT_PDF_FOR_SIGNATURE, 'Sent PDF for Signature'),
    (SENT_RECVD_CONTRACT, 'Sent/Received Contract'),
    (APPROVED_BY_CREDIT_MANAGER, 'Approved by Credit Manager'),
    (REJECTED_BY_CREDIT_MANAGER, 'Rejected by Credit Manager'),
    (ALL_SIGNATURE_APPROVAL_RECVD, 'All Signatures and Approvals Received'),
    (IO_ACTIVE, 'Active'),
    (IO_COMPLETE, 'Complete'),
    )


PEERTOPEER_VERTICAL = 0
PEERTOPEER_ADVERTISER = 1
PEERTOPEER_ADVERTISER_VERTICAL = 2
PEERTOPEER_PUBLISHER = 3
PEERTOPEER_PUBLISHER_VERTICAL = 4

PEERTOPEER_ADVERTISER_CHOICES = (
    (PEERTOPEER_VERTICAL, 'Same Vertical'),
    (PEERTOPEER_PUBLISHER, 'Same Publishers'),
    (PEERTOPEER_PUBLISHER_VERTICAL, 'Same Publisher Vertical'),
)

PEERTOPEER_PUBLISHER_CHOICES = (
    (PEERTOPEER_VERTICAL, 'Same Vertical'),
    (PEERTOPEER_ADVERTISER, 'Same Advertisers'),
    (PEERTOPEER_ADVERTISER_VERTICAL, 'Same Advertiser Vertical'),
)

PEERTOPEERPERIOD_HOURLY = 0
PEERTOPEERPERIOD_DAILY = 1

PEERTOPEERPERIOD_CHOICES = (
    (PEERTOPEERPERIOD_HOURLY, 'Hourly'),
    (PEERTOPEERPERIOD_DAILY, 'Daily'),
)


SERVERSTATUS_OK = 0
SERVERSTATUS_ERROR = 1

SERVERSTATUS_CHOICES = (
    (SERVERSTATUS_OK, 'OK'),
    (SERVERSTATUS_ERROR, 'ERROR'),
)


AQ_WIDGET = 1
PIWIK_WIDGET = 2
WIDGET_TYPES = (
    (AQ_WIDGET, 'Aquotient'),
    (PIWIK_WIDGET, 'Piwik'),
)

WIDGET_FUNCTIONS = (
	(1,'getSumVisitsLength'),
	(2,'getBrowserType'),
	(3,'getWebsites'),
	(4,'getKeywords'),
	('Referers/getSearchEngines','Referers/getSearchEngines'),
	('VisitTime/getVisitInformationPerServerTime','VisitTime/getVisitInformationPerServerTime'),
	(7,'getCountry'),
	('VisitsSummary/getVisits','VisitsSummary/getVisits'),
	(9,'getOS'),
	('Referers/getRefererType','Referers/getRefererType' ),
)

CHART_STYLES = (
    ('lines', 'lines'),
    ('columns', 'columns'),
    ('pie', 'pie'),
    ('table', 'table')
)

INQUIRY_DENIAL_REASONS = (
    ('','-------------'),
    ('Manual Credit','Manual Credit'),
    ('Denied : No Access to Data Due to Age of Transaction','Denied : No Access to Data Due to Age of Transaction'),
    ('Denied : Non-Commissionable','Denied : Non-Commissionable'),
    ('Denied : Non-Commissionable Coupon Code Used','Denied : Non-Commissionable Coupon Code Used'),
    ('Denied : Order Not Yet Shipped','Denied : Order Not Yet Shipped'),
    ('Denied : Order Was Cancelled','Denied : Order Was Cancelled'),
    ('Denied : Return Days Exceeded','Denied : Return Days Exceeded'),
    ('Denied : Transaction Referred by Another Affiliate','Denied : Transaction Referred by Another Affiliate'),
    ('Other : Cannot Locate Order ID','Other : Cannot Locate Order ID'),
    ('Other : Advertiser Previously Paid','Other : Advertiser Previously Paid'),
    ('Other : Advertiser to Contact Affiliate Directly','Other : Advertiser to Contact Affiliate Directly'),
    ('comments','Other : See Comments'),
    

)

#BrandLock Report Types
BLR_RANK = 'rank'
BLR_MARKET_SHARE = 'market_share'
BLR_DAY_PART = 'day_part'
BLR_COPY_CHANGES = 'copy_changes'
BLR_COPY_DETAILS = 'copy_details'
BLR_KEYWORD_DETAILS = 'keyword_details'
BLR_KEYWORD = 'keyword'
BLR_OFFER_KEYWORDS = 'offer_keywords'
BLR_OFFER_AVERTISERS = 'offer_advertisers'
BLR_LISTING_DETAILS = 'listing_details'
BLR_LISTING = 'listing'
BLR_TRADEMARK = 'trademark'
BLR_TRADEMARK_DETAILS = 'trademark_details'
BLR_HIGHJACKS = 'url_highjacks'
BLR_HIGHJACKS_DETAILS = 'url_highjacks_details'
BLR_AFFILIATE = 'affiliate'
BLR_AFFILIATE_DETAILS = 'affiliate_details'

BLR_CHOICES = (
    (BLR_RANK, 'Rank'),
    (BLR_DAY_PART, 'Day Part'),
    (BLR_MARKET_SHARE, 'Market Share'),
    (BLR_COPY_CHANGES, 'Copy Changes'),
    (BLR_COPY_DETAILS, 'Copy Details'),
    (BLR_KEYWORD, 'Keyword'),
    (BLR_KEYWORD_DETAILS, 'Keyword Details'),
    (BLR_OFFER_KEYWORDS, 'Offer Keywords'),
    (BLR_OFFER_AVERTISERS, 'Offer Advertisers'),
    (BLR_LISTING_DETAILS, 'Listing Details'),
    (BLR_LISTING, 'Listing'),
    (BLR_TRADEMARK, 'Trademark'),
    (BLR_TRADEMARK_DETAILS, 'Trademark Details'),
    (BLR_HIGHJACKS, 'URL HighJacks'),
    (BLR_HIGHJACKS_DETAILS, 'URL HighJacks Details'),
    (BLR_AFFILIATE, 'Affiliate'),
    (BLR_AFFILIATE_DETAILS, 'Affiliate Details'),
    
)

#BrandLock Search Provider Types
BLS_PROVIDERS = (
    ('Google', 'Google'),
    ('Microsoft', 'Microsoft'),
    ('Yahoo', 'Yahoo'),
)
BLS_PROVIDERS_EDIT = (
    ('1', 'Google'),
    ('2', 'Microsoft'),
    ('3', 'Yahoo'),
)

#BrandLock Time Periods
BLR_TIME = (
	('0', 'Select One'),
    ('today', 'today'),
    ('yesterday', 'yesterday'),
    ('last7days', 'last7days'),
    ('thismonth', 'thismonth'),
    ('last30days', 'last30days'),
    ('lastmonth', 'lastmonth'),
)

BLR_LIST_ATT = (
    ('indented', 'indented'),
    ('map', 'map'),
    ('stock_quote', 'stock_quote'),
    ('paid_inclusion', 'paid_inclusion'),
    ('sublinks', 'sublinks'),
    ('video', 'video'),
    ('image', 'image'),
)
BLR_LIST_ATT_RAT = (
    ('No Rating', 'No Rating'),
    ('0 - 9% Positive', '0 - 9% Positive'),
    ('10 - 19% Positive', '10 - 19% Positive'),
    ('20 - 29% Positive', '20 - 29% Positive'),
    ('30 - 39% Positive', '30 - 39% Positive'),
    ('40 - 49% Positive', '40 - 49% Positive'),
    ('50 - 59% Positive', '50 - 59% Positive'),
    ('60 - 69% Positive', '60 - 69% Positive'),
    ('70 - 79% Positive', '70 - 79% Positive'),
    ('80 - 89% Positive', '80 - 89% Positive'),
    ('90 - 100% Positive', '90 - 100% Positive'),
)

BLR_LIST_ATT_REV = (
    ('No Reviews', 'No Reviews'),
    ('< 10 Reviews', '< 10 Reviews'),
    ('10 - 20 Reviews', '10 - 20 Reviews'),
    ('21 - 50 Reviews', '21 - 50 Reviews'),
    ('> 50 Reviews', '> 50 Reviews'),
)

BLR_LIST_SEC = (
    ('Blogs', 'Blogs'),
    ('Books', 'Books'),
    ('Images', 'Images'),
    ('Local', 'Local'),
    ('Main', 'Main'),
    ('News', 'News'),
    ('Profiles', 'Profiles'),
    ('Shopping', 'Shopping'),
    ('Spelling', 'Spelling'),
    ('Videos', 'Videos'),
)

BLR_OFFER_TYPE = (
	('0', 'Select One'),
    ('Free Shipping', 'Free Shipping'),
    ('Discount Shipping', 'Discount Shipping'),
    ('Free Trial', 'Free Trial'),
    ('Sale', 'Sale'),
    ('In-Store', 'In-Store'),
    ('Cash Back', 'Cash Back'),
    ('Gift Card', 'Gift Card'),
    ('Subscription', 'Subscription'),
    ('Free Product', 'Free Product'),
)

SRCHPUBORDERSBY_ALL = 0
SRCHPUBORDERSBY_SPECIFIC = 1

SRCHPUBORDERSBY_CHOICES = (
        (SRCHPUBORDERSBY_ALL, 'All'),
        (SRCHPUBORDERSBY_SPECIFIC, 'Specific'),
    )
    
ORDERAMTSBY_ALL = 0
ORDERAMTSBY_GREATER_THAN = 1
ORDERAMTSBY_LESS_THAN = 2
ORDERAMTSBY_EQUAL_TO = 3

ORDERAMTSBY_CHOICES = (
        (ORDERAMTSBY_ALL, 'All amounts'),
        (ORDERAMTSBY_GREATER_THAN, 'Greater than'),
        (ORDERAMTSBY_LESS_THAN, 'Less than'),
        (ORDERAMTSBY_EQUAL_TO, 'Equal to'),
    )


CREATEORDER_FEES_SYSTEMCALCULATED = 0
CREATEORDER_FEES_CUSTOM  = 1

CREATEORDER_FEES = (
        (CREATEORDER_FEES_SYSTEMCALCULATED, 'Let the system calculate fees based on the order amount'),
        (CREATEORDER_FEES_CUSTOM, 'Set the fees on my own'),
    )
######################### Custom Error Messages ###########################
SIGNUP_INVALID_LINK = """ Sorry but the link you clicked to get here is no longer valid.<br><br>
                        If you would like help registering to Atrinsic Affiliate Network you can contact us at  <a href="mailto:admin@network.atrinsic.com" style="color:red;">admin@network.atrinsic.com</a>."""
                        
RSS_TIMEOUT = """ The RSS Feed you are requesting has timed out. Please try again shortly.<br><br>
                        If you require immediate assistance, please contact us at  <a href="mailto:admin@network.atrinsic.com" style="color:red;">admin@network.atrinsic.com</a>."""
