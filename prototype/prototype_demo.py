import streamlit as st
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import altair as alt
from PIL import Image

def get_review_summaries(product_id, product_type, reviews_df):
    filtered_reviews = reviews_df[(reviews_df['product_id'] == product_id) & (reviews_df['product_type'] == product_type)]

    positive_summary = "해당 리뷰는 아직 준비 중입니다."
    negative_summary = "해당 리뷰는 아직 준비 중입니다."

    for _, row in filtered_reviews.iterrows():
        sentiment = row['sentiment']
        summary = row['summary']
        if sentiment == 'positive':
            positive_summary = summary
        elif sentiment == 'negative':
            negative_summary = summary

    return positive_summary, negative_summary

def get_review_sentiment(product_id, product_type, reviews_df):
    filtered_reviews = reviews_df[(reviews_df['product_id'] == product_id) & (reviews_df['product_type'] == product_type)]

    positive_percent = 0
    negative_percent = 0

    for _, row in filtered_reviews.iterrows():
        sentiment = row['sentiment']
        percent = row['sentiment_ratio']
        if sentiment == 'positive':
            positive_percent = percent
        elif sentiment == 'negative':
            negative_percent = percent

    return positive_percent, negative_percent

def get_receipe_summaries(product_id, recipes_df):
    filtered_recipes = recipes_df[recipes_df['product_id'] == product_id]

    if not filtered_recipes.empty:
        summaries = []
        for product_type in filtered_recipes['product_type'].unique():
            product_summary = filtered_recipes[filtered_recipes['product_type'] == product_type]['summary'].tolist()

            if product_summary:
                summary_text = ' '.join(product_summary)
            else:
                summary_text = '해당 리뷰는 아직 준비 중입니다.'

            summaries.append(f"<strong style='color: #5F0080;'>{product_type}</strong><br>"
                             f"<div style='background-color: #E6E6FA; padding: 10px; border-radius: 5px; margin: 5px 0;'>"
                             f"{summary_text}</div>")

        return ''.join(summaries)
    else:
        return "<div style='background-color: #E6E6FA; padding: 10px; border-radius: 5px; margin: 5px 0;'>No recipes available for this product.</div>"

def get_category_reviews(product_id, category, recipes_df):
    filtered_recipes = recipes_df[recipes_df['product_id'] == product_id]

    if not filtered_recipes.empty:
        filtered_recipes = filtered_recipes[filtered_recipes['category'] == category]

        if not filtered_recipes.empty:
            summaries = []
            for product_type in filtered_recipes['product_type'].unique():
                product_summaries = filtered_recipes[filtered_recipes['product_type'] == product_type]['summary'].tolist()

                summary_text = ' '.join(product_summaries)

                summaries.append(
                    f"<p style='color: #5F0080;'><strong>{product_type}</strong></p>"
                    f"<div style='background-color: #BD76FF14; padding: 10px; border-radius: 5px; margin: 5px 0;'>"
                    f"{summary_text}</div>"
                )

            return ''.join(summaries)
        else:
            return "<div style='background-color: #BD76FF14; padding: 10px; border-radius: 5px; margin: 5px 0;'>해당 리뷰는 아직 준비 중입니다.</div>"
    else:
        return "<div style='background-color: #BD76FF14; padding: 10px; border-radius: 5px; margin: 5px 0;'>해당 리뷰는 아직 준비 중입니다.</div>"


def create_box(content, background_color):
    return f"""
    <div style="background-color: {background_color}; padding: 10px; border-radius: 10px; margin-bottom: 10px;">
        {content}
    </div>
    """

def get_driver(headless=True):
    driver = Driver(browser="chrome", headless=True)

    return driver

def get_product_info(driver, product_id):
    product_url = f'https://www.kurly.com/goods/{product_id}'
    driver.get(product_url)

    try:
        name = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#product-atf > section > div.css-1qy9c46.ezpe9l12 > h1'))
        ).text

        price = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#product-atf > section > h2'))
        ).text

        delivery = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#product-atf > section > ul > li:nth-child(3) > dd > p.css-c02hqi.e6qx2kx1'))
        ).text

        image_url = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#product-atf > div > div > div > div > div > span > img'))
        ).get_attribute('src')

        detail_list = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#detail > div.css-kqvkc7.es6jciw1 > img'))
        ).get_attribute('src')

        return {
            'name': name,
            'price': price,
            'image_url': image_url,
            'details': detail_list,
            'dd': delivery,
            'product_url': product_url
        }
    except Exception as e:
        print(f"Error fetching product info: {e}")
        return None
    finally:
        driver.quit()

def fetch_product_image_url(driver, product_id):
    product_url = f'https://www.kurly.com/goods/{product_id}'
    driver.get(product_url)

    try:
        image_url = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#product-atf > div > div > div > div > div > span > img'))
        ).get_attribute('src')

        return image_url
    except Exception as e:
        print(f"Error fetching product image for {product_id}: {e}")
        return None

def fetch_product_names(driver, product_id):
    product_url = f'https://www.kurly.com/goods/{product_id}'
    driver.get(product_url)

    try:
        name = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#product-atf > section > div.css-1qy9c46.ezpe9l12 > h1'))
        ).text

        return name
    except Exception as e:
        print(f"Error fetching product image for {product_id}: {e}")
        return None


def make_donut(input_response, input_text, input_color):
    color_map = {
        'green': ['#27AE60', '#12783D'],
        'red': ['#E74C3C', '#781F16']
    }

    chart_color = color_map.get(input_color, ['#cccccc', '#666666'])

    source = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100 - input_response, input_response]
    })

    source_bg = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100, 0]
    })

    plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
        theta="% value",
        color=alt.Color("Topic:N",
                        scale=alt.Scale(
                            domain=[input_text, ''],
                            range=chart_color),
                        legend=None),
    ).properties(width=130, height=130)

    text = plot.mark_text(
        align='center',
        color="#29b5e8",
        font="Lato",
        fontSize=32,
        fontWeight=700,
        fontStyle="italic"
    ).encode(text=alt.value(f'{input_response} %'))

    plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
        theta="% value",
        color=alt.Color("Topic:N",
                        scale=alt.Scale(
                            domain=[input_text, ''],
                            range=chart_color),
                        legend=None),
    ).properties(width=130, height=130)

    return plot_bg + plot + text

def main():
    driver = get_driver()
    st.title("🔮 마켓컬리 리뷰 요약 서비스 🔮")
    st.markdown("<style>div.stButton > button {width: 100%;}</style>", unsafe_allow_html=True)

    reviews_df = pd.read_csv('emotion_summary_10.csv')
    recipes_df = pd.read_csv('category_summary_10.csv')
    recipes = pd.read_csv('receipe_summary_10.csv')

    product_input = st.text_input('상품 ID 입력해주세요', value=st.session_state.get('product_input', ''),
                                  placeholder='🔍 상품 ID를 입력해주세요...')

    if 'product_info' not in st.session_state:
        st.session_state.product_info = None
    if 'show_details' not in st.session_state:
        st.session_state.show_details = False
    if 'product_input' not in st.session_state:
        st.session_state.product_input = ""
    if 'show_top_10' not in st.session_state:
        st.session_state.show_top_10 = False

    if product_input and product_input != st.session_state.get('product_input'):
        st.session_state.product_input = product_input
        if int(product_input) not in reviews_df['product_id'].values:
            st.warning("해당 상품 ID는 존재하지 않습니다. 다시 입력해주세요.")
        else:
            st.session_state.product_info = get_product_info(driver, product_input)

    if st.session_state.product_info:
        st.subheader("상품 정보")

        col_image, col_details = st.columns([1, 2])

        with col_image:
            st.image(st.session_state.product_info['image_url'], width=200)

        with col_details:
            st.write(f"**상품명:** {st.session_state.product_info['name']}")
            st.write(f"**배송:** {st.session_state.product_info['dd']}")
            st.write(f"**가격:** {st.session_state.product_info['price']}")

            if st.button('상세 정보 이미지'):
                st.session_state.show_details = not st.session_state.show_details

            if st.session_state.show_details:
                st.image(st.session_state.product_info['details'], width=500)

            st.markdown(
                f'<a href="{st.session_state.product_info["product_url"]}" target="_blank" style="display: block; text-align: center; padding: 10px; background-color: #5F0080; color: white; border: none; border-radius: 5px; text-decoration: none;">구매하기</a>',
                unsafe_allow_html=True
            )
        product_reviews = reviews_df[reviews_df['product_id'] == int(product_input)]
        product_types = product_reviews['product_type'].unique()

        st.markdown("---")

        st.subheader("상품 리뷰")

        for product_type in product_types:
            st.markdown(
                f'<p style="font-size: 18px; color: #5F0080; background-color: #BD76FF14; padding: 5px; border-radius: 5px;"><strong>{product_type}</strong></p>',
                unsafe_allow_html=True
            )

            positive_summary, negative_summary = get_review_summaries(int(product_input), product_type, reviews_df)

            if not positive_summary and not negative_summary:
                st.write("준비중입니다.")
            else:
                positive_percent, negative_percent = get_review_sentiment(int(product_input), product_type, reviews_df)

                col1, col2 = st.columns([0.4, 2])

                with col1:
                    st.altair_chart(make_donut(positive_percent, "긍정", "green"), use_container_width=True)

                with col2:
                    st.markdown(
                        create_box(
                            f"<div style='white-space: normal; word-wrap: break-word;'>😊 {positive_summary if positive_summary else '준비중입니다.'}</div>",
                            "#EDEDED"),
                        unsafe_allow_html=True
                    )

                col1, col2 = st.columns([0.4, 2])

                with col1:
                    st.altair_chart(make_donut(negative_percent, "부정", "red"), use_container_width=True)

                with col2:
                    st.markdown(
                        create_box(
                            f"<div style='white-space: normal; word-wrap: break-word;'>😔 {negative_summary if negative_summary else '준비중입니다.'}</div>",
                            "#EDEDED"),
                        unsafe_allow_html=True
                    )

        st.write("")
        st.markdown(
            '<p style="font-size:20px;"><strong>🍽️맛잘알 추천 레시피🍽️</strong></p>',
            unsafe_allow_html=True
        )

        recipe_summary = get_receipe_summaries(int(product_input), recipes)

        st.markdown(
            f"""
            <div style='border: 2px solid #D3D3D3; padding: 10px; border-radius: 10px; background-color: #F8F8FF;'>
                {recipe_summary}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")
        st.write("")
        category = st.selectbox("카테고리를 선택해주세요", ['맛/향/풍미', '보관', '포장/배송', '양', '가격'])
        category_summary = get_category_reviews(int(product_input), category, recipes_df)
        st.markdown(category_summary, unsafe_allow_html=True)

    if st.session_state.product_info is None:
        category_selection = st.selectbox("카테고리를 선택해주세요", ["국/탕/찌개", "밑반찬", "김치/젓갈/장류", "두부/어묵/부침개", "메인요리"])

        if category_selection == "국/탕/찌개":
            st.session_state.show_top_10 = True
            st.subheader("⭐TOP 10⭐")
            image = Image.open("top.jpg")
            st.image(image, use_column_width=True)

if __name__ == "__main__":
    main()