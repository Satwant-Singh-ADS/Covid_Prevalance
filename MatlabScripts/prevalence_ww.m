%% Fetch/Read data
clear;
sel_url = 'https://raw.githubusercontent.com/biobotanalytics/covid19-wastewater-data/master/wastewater_by_county.csv';
urlwrite(sel_url, 'dummy.csv');
ww_data = readtable('dummy.csv');
abvs = readcell('us_states_abbr_list.txt');
fips_tab = readtable('fips_table.txt', 'Format', '%s%s%s%d');
load latest_us_data.mat %THIS SHOULD BE UPDATED CONSISTENTLY. SHOULD BE ON GITHUB BUT NOT BEING UPDATED: https://github.com/scc-usc/ReCOVER-COVID-19/tree/master/matlab%20scripts. FOR NOW CAN GET FROM SERVER IF NEED BE
%%
fips_tab.location(strcmpi(fips_tab.location, 'US')) = {'0'}; %Change US code to 0
[aa, fips_idx] = ismember(ww_data.fipscode, cellfun(@(x)(str2double(x)), fips_tab.location)); %Get indices of fips code available in ww_data table and fips_tab table

xx = ww_data.sampling_week; %sampling_week column values

%Set whichday to be array of day # correspodning to day since 2020,1,23
whichday = zeros(length(xx), 1); 
for ii = 1:length(xx)
    whichday(ii) = days(xx(ii) - datetime(2020, 1, 23));
end

%Define 2 matrices of size = (# of states x days)
ww_ts = zeros(size(data_4));
ww_pres = zeros(size(data_4));

[aa, abvs_idx] = ismember(ww_data.state, abvs); %Get inicies of states according to abvs

for ii=1:length(xx)
    if whichday(ii) < 1 || fips_idx(ii) < 1 %ignore dates before 2020,1,23 and unavailable states
        continue;
    end
    ww_pres(abvs_idx(ii), whichday(ii)) = 1; %Set to 1 if data available for state/day
    % fill other matrix with effective_concentration_rolling_average*(pop
    % of county / pop of state)
    ww_ts(abvs_idx(ii), whichday(ii)) = ww_ts(abvs_idx(ii), whichday(ii)) ...
        + ww_data.effective_concentration_rolling_average(ii)*fips_tab.population(fips_idx(ii))/popu(abvs_idx(ii));
end
ww_ts(ww_pres < 1) = nan; %Set any ww_ts data to nan if no data available in ww_pres
ww_ts(ww_ts <= 0) = nan;%Set any ww_ts data to nan if <=0
%%
ww_ts1 = fillmissing(ww_ts, 'linear', 2, 'EndValues','none'); %Fill missing values with linear interpolation with a moving mean of winodw size = 2 and without filling endpoints
ww_tsm = movmean(ww_ts1, 14, 2); %use movingmean filter to smooth
data_4_s = smooth_epidata(data_4, 14, 0, 1); %Use custom smooth_epidata to filter
data_diff = [zeros(length(popu), 1) diff(data_4_s, 1, 2)]; %Let day 0=0s and instead of having cumilative cases up to day, use diff to find daily cases at day x
%%
%I believe the first starts at 6 and the second at 3 to make the weeks both
%start on Sunday (This is basically hard coded i belive, we will need to
%heck)
ww_tsw = [zeros(length(popu), 1) ww_ts(:, 6:7:end)]; %ww_ts is also cumilative data, so making first entries 0 & ignoring first couple entries & then skipping each 7 afterwards makes this weekly values
weekly_dat = [zeros(length(popu), 1) diff(data_4_s(:, 3:7:end), 1, 2)]; %Also make this weekly data as above

%% 
wlag = 7; 
ww_tsm(ww_ts==0) = nan; %Set 0 values to nan
f = nan(size(ww_ts));
f(:, 1+wlag:end) = ww_ts(:, 1:end-wlag)./data_diff(:, 1+wlag:end); %add a lag
f(:, 1:200) = nan;
f1 = f;
% f = fillmissing(f, "linear", 2, 'EndValues','none');
% f = filloutliers(f, "linear", 2);
% f = fillmissing(f, "nearest", 2);

for jj = 1:size(ww_ts, 1)
    xx = find(~isnan(f1(jj, :))); %Get non-nan indicies in f1(jj,:)
    yy = f1(jj, xx); %get only non nan values in f1(jj,:)
    if length(xx) > 5 && sum(xx > 200 & xx < 600) > 2
        f(jj, 200:end) = csaps(xx, yy, 0.0001, 200:size(f, 2)); %This does subic spline smoothing (Available in python)
    end
    f(jj, :) = fillmissing(f(jj, :), "linear", 1, 'EndValues','none'); %Linear interpolation without smoothing
    %f(jj, :) = filloutliers(f(jj, :), "linear");
    f(jj, :) = fillmissing(f(jj, :), "nearest"); %fill missing values with just the nearest value
end

%set values < 0 to 0 & use moveing mean smoothing
f(f<0) = 0; f = movmean(f, 7, 2);
ww_adj = movmean(data_diff.*f, 14, 2);
%% Load seroprevaelnce data
CDC_sero; %Run CDC_sero script and save variables to workspace for use on this script
%%

%Keep all positive values & set the negatives to 0
true_new_infec{1} = (true_new_infec{1}+abs(true_new_infec{1}))/2;
true_new_infec{2} = (true_new_infec{2}+abs(true_new_infec{2}))/2;
true_new_infec{3} = (true_new_infec{3}+abs(true_new_infec{3}))/2;

eq_range = 200:600; % This is the range to use for calibration of wastewate concentration
nz_idx =  ww_adj(:, eq_range)>0.5; % To deal with missing data early (Filter out anything less than that 0.5 value)

ww_year1 = sum(ww_adj(:, eq_range).*nz_idx, 2); %sum of non missing data across 2nd dimension

%For each year, find some of none missing data as above and divide it by ww
%then multiply by ww_adj before smoothing
sero_year1 = sum(true_new_infec{2}(:, eq_range).*nz_idx, 2); %This might need to be 1? there might be a typo
true_new_infec_ww{1} = [(sero_year1./ww_year1).*ww_adj];
true_new_infec_ww{1} = movmean(max(true_new_infec_ww{1}, max(true_new_infec{1},un_array(:, 1).*data_diff)), 14, 2);

sero_year2 = sum(true_new_infec{2}(:, eq_range).*nz_idx, 2);
true_new_infec_ww{2} = [(sero_year2./ww_year1).*ww_adj];
true_new_infec_ww{2} = movmean(max(true_new_infec_ww{2}, max(true_new_infec{2},un_array(:, 2).*data_diff)), 14, 2);

sero_year3 = sum(true_new_infec{3}(:, eq_range).*nz_idx, 2);
true_new_infec_ww{3} = [(sero_year3./ww_year1).*ww_adj];
true_new_infec_ww{3} = movmean(max(true_new_infec_ww{3}, max(true_new_infec{3},un_array(:, 3).*data_diff)), 14, 2);

%replace bad states
bad_states = (sum(~isnan(ww_ts), 2)<1) & (sum(~isnan(true_new_infec{2}), 2)>1);
true_new_infec_ww{1}(bad_states, :) = true_new_infec{1}(bad_states, :); true_new_infec_ww{2}(bad_states, :) = true_new_infec{2}(bad_states, :); true_new_infec_ww{3}(bad_states, :) = true_new_infec{3}(bad_states, :);

bad_states = (sum(~isnan(ww_ts), 2)<1) & (sum(~isnan(true_new_infec{2}), 2)<1);
true_new_infec_ww{1}(bad_states, :) = data_diff(bad_states, :); true_new_infec_ww{2}(bad_states, :) = data_diff(bad_states, :); true_new_infec_ww{3}(bad_states, :) = data_diff(bad_states, :);
%% save true_new_infec_ww, true_new_infec variables
save ww_prevalence_us.mat true_new_infec_ww true_new_infec;
