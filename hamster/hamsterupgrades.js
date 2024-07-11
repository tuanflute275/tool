const axios = require('axios');
const fs = require('fs');
const readline = require('readline');

const csvDataAuth = fs.readFileSync('authorization.csv', 'utf8');
const authorizationList = csvDataAuth.split('\n').map(line => line.trim()).filter(line => line !== '');
const dieukien = 100000;

function createAxiosInstance() {
    return axios.create({
        baseURL: 'https://api.hamsterkombat.io',
        timeout: 10000,
        headers: {
            'Content-Type': 'application/json'
        }
    });
}

async function getBalanceCoins(dancay, authorization) {
    try {
        const response = await dancay.post('/clicker/sync', {}, {
            headers: {
                'Authorization': `Bearer ${authorization}`
            }
        });

        if (response.status === 200) {
            return response.data.clickerUser.balanceCoins;
        } else {
            console.error('Không lấy được thông tin balanceCoins. Status code:', response.status);
            return null;
        }
    } catch (error) {
        console.error('Error:', error);
        return null;
    }
}

async function buyUpgrades(dancay, authorization) {
    try {
        const upgradesResponse = await dancay.post('/clicker/upgrades-for-buy', {}, {
            headers: {
                'Authorization': `Bearer ${authorization}`
            }
        });

        if (upgradesResponse.status === 200) {
            const upgrades = upgradesResponse.data.upgradesForBuy;
            let balanceCoins = await getBalanceCoins(dancay, authorization);
            let purchased = false;

            for (const upgrade of upgrades) {
                if (upgrade.cooldownSeconds > 0) {
                    console.log(`Thẻ ${upgrade.name} đang trong thời gian cooldown ${upgrade.cooldownSeconds} giây.`);
                    continue; 
                }

                if (upgrade.isAvailable && !upgrade.isExpired && upgrade.price < dieukien && upgrade.price <= balanceCoins) {
                    const buyUpgradePayload = {
                        upgradeId: upgrade.id,
                        timestamp: Math.floor(Date.now() / 1000)
                    };
                    try {
                        const response = await dancay.post('/clicker/buy-upgrade', buyUpgradePayload, {
                            headers: {
                                'Authorization': `Bearer ${authorization}`
                            }
                        });
                        if (response.status === 200) {
                            console.log(`(${Math.floor(balanceCoins)}) Đã nâng cấp thẻ ${upgrade.name} cho token ${authorization}.`);
                            purchased = true;
                            balanceCoins -= upgrade.price; 
                        }
                    } catch (error) {
                        if (error.response && error.response.data && error.response.data.error_code === 'UPGRADE_COOLDOWN') {
                            console.log(`Thẻ ${upgrade.name} đang trong thời gian cooldown ${error.response.data.cooldownSeconds} giây.`);
                            continue; 
                        } else {
                            throw error;
                        }
                    }
                    await new Promise(resolve => setTimeout(resolve, 1000)); 
                }
            }

            if (!purchased) {
                console.log(`Token ${authorization.substring(0, 10)}... không có thẻ nào khả dụng hoặc đủ điều kiện. Chuyển token tiếp theo...`);
                return false;
            }
        } else {
            console.error('Không lấy được danh sách thẻ. Status code:', upgradesResponse.status);
            return false;
        }
    } catch (error) {
        console.error('Lỗi không mong muốn, chuyển token tiếp theo');
        return false;
    }
    return true;
}

async function claimDailyCipher(dancay, authorization, cipher) {
    if (cipher) {
        try {
            const payload = {
                cipher: cipher
            };
            const response = await dancay.post('/clicker/claim-daily-cipher', payload, {
                headers: {
                    'Authorization': `Bearer ${authorization}`
                }
            });

            if (response.status === 200) {
                console.log(`Đã claim daily cipher với mã ${cipher} cho token ${authorization}`);
            } else {
                console.error('Không claim được daily cipher. Status code:', response.status);
            }
        } catch (error) {
            console.error('Mã morse đã được giải');
        }
    }
}

async function runForAuthorization(authorization, cipher) {
    const dancay = createAxiosInstance();

    await claimDailyCipher(dancay, authorization, cipher);

    while (true) {
        const success = await buyUpgrades(dancay, authorization);
        if (!success) {
            break;
        }
    }
}

async function askForCipher() {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    return new Promise(resolve => {
        rl.question('Mã morse hôm nay cần giải: ', (answer) => {
            rl.close();
            resolve(answer.trim());
        });
    });
}

async function main() {
    const cipher = await askForCipher();
    for (const authorization of authorizationList) {
        await runForAuthorization(authorization, cipher);
    }
    console.log('Đã chạy xong tất cả các token.');
}

main();
